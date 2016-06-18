# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
import openerp.addons.decimal_precision as dp
import openerp.exceptions
from openerp import netsvc
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

def str_to_datetime(strdate):
    return datetime.datetime.strptime(strdate, tools.DEFAULT_SERVER_DATE_FORMAT)

class account_invoice(osv.osv):

    '''Herencia del modelo account.invoice para realizar ajustes necesarios en Akr 58 C.A. '''
    _name = "account.invoice"
    _inherit = "account.invoice"


    def action_move_create(self, cr, uid, ids, context=None):
        print "<<<<<<<<<< En action_move_create >>>>>>>>>>>>>>>>>>>>>> "
        '''Metodo heredado para realizar la creacion del comprobante de retencion del proveedor al validar la factura. '''
        res = super(account_invoice, self).action_move_create(cr, uid, ids, context=context)
        con = cr.execute(''' select  MAX(number) FROM account_wh_iva ''')
        con = cr.fetchone()
        value = con and con[0] or time.strftime('%Y%m')+'0'
        code = time.strftime('%Y%m')+str(int(value[6:])+1).zfill(8)

        invoice_tax_obj = self.pool.get('account.invoice.tax')
        wh_iva_obj = self.pool.get('account.wh.iva')
        wh_iva_line_obj = self.pool.get('account.wh.iva.line')
        account_obj = self.pool.get('account.account')

        invoice = self.browse(cr, uid, ids, context=context)[0]

        #validamos que el documento sea factura de compra o N/C-N/D de proveedor
        if invoice.type <> 'out_invoice' and invoice.journal_id.type in ('purchase','purchase_refund','purchase_debit'):
            inv_tax_ids = invoice_tax_obj.search(cr, uid, [('invoice_id','=',invoice.id)], context=context)

            #verificamos si ya existe un comprobante generado para el proveedor con la fecha en curso
            #wh_iva_val = wh_iva_obj.search(cr, uid, [('partner_id','=',invoice.partner_id.id),('date_ret','=',time.strftime('%Y-%m-%d'))], context=context)

            if inv_tax_ids: #verificamos si el documento tiene impuestos
                base = 0
                ret = 0
                for i in invoice_tax_obj.browse(cr, uid, inv_tax_ids, context=context):
                    if i.tax_id.withholding:
                        base = i.base
                        ret = i.amount
                        name = i.name
                        inv_tax_id = i.id
                        account = i.tax_id.account_collected_id.id
                lines = {
                            'inv_tax_id': inv_tax_id,
                            'amount_ret': ret,
                          }
                details = {
                            'name': name,
                            'move_id': invoice.move_id.id,
                            'invoice_id': ids[0],
                            'amount_ret': ret,
                            'tax_line': [(0,0,lines)]
                          }
                vals_wh = {
                            'partner_id': invoice.partner_id.id,
                            'period_id': invoice.period_id.id,
                            'journal_id': invoice.journal_id.id,
                            'account_id': account,
                            'fortnight':int(time.strftime('%d')) >= 15 and 'True' or 'False',
                            'date_ret':time.strftime('%Y-%m-%d'),
                            'number':code,
                            'name': 'Retencion IVA '+str(invoice.partner_id.name),
                            'code': code[6:],
                            'date':time.strftime('%Y-%m-%d'),
                            'amount_base_ret': base,
                            'type': invoice.type,
                            'total_tax_ret': ret,
                            'wh_lines': [(0,0,details)]
                            }
                #~ if wh_iva_val:
                    #~ wh_iva_obj.write(cr, uid, wh_iva_val, { 'wh_lines': [(0,0,details)] })
                #~ else:
                    #~ wh_iva_obj.create(cr, uid, vals_wh, context=context)
        return res

    def compute_invoice_totals(self, cr, uid, inv, company_currency, ref, invoice_move_lines, context=None):
        print "<<<<<<<<<< En compute_invoice_totals >>>>>>>>>>>>>>>>>>>>>> "
        '''Herencia: Funcion que calcula los totales que ingresan al comprobante contable cuando se
                     valida la factura. (se le agrego una condicion para que reste y registre como un
                     credito el monto de las retenciones)'''
        if context is None:
            context={}
        atax_obj = self.pool.get('account.tax')
        total = 0
        total_currency = 0
        cur_obj = self.pool.get('res.currency')
        for i in invoice_move_lines:
            if inv.currency_id.id != company_currency:
                context.update({'date': inv.date_invoice or time.strftime('%Y-%m-%d')})
                i['currency_id'] = inv.currency_id.id
                i['amount_currency'] = i['price']
                i['price'] = cur_obj.compute(cr, uid, inv.currency_id.id,
                        company_currency, i['price'],
                        context=context)
            else:
                i['amount_currency'] = False
                i['currency_id'] = False
            i['ref'] = ref
            if inv.type in ('out_invoice','in_refund'):
                total += i['price']
                total_currency += i['amount_currency'] or i['price']
                i['price'] = - i['price']
            else:
                if i['type'] == 'tax': #condicion agregada
                    tax_id = atax_obj.search(cr, uid, [('account_collected_id','=',i['account_id']),('name','=',i['name'])], context=context)
                    atax_read = atax_obj.read(cr, uid, tax_id, ['withholding'], context=context)
                    res_tax = atax_read and atax_read[0] or False
                    if res_tax and res_tax['withholding'] is True and i['price']>0:
                        i.update({'price': i['price']*-1})
                total -= i['price']
                total_currency -= i['amount_currency'] or i['price']
        return total, total_currency, invoice_move_lines

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        print "<<<<<<<<<< En _amount_all >>>>>>>>>>>>>>>>>>>>>> "
        '''Herencia: Funcion que calcula los totales de la factura. (se le agrego una condicion para que
                     sume solo los montos de los impuestos padre, es decir, no totalice retenciones)'''
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_discount': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += line.price_subtotal
            res[invoice.id]['amount_discount'] += res[invoice.id]['amount_untaxed'] * ((invoice.discount or 0.0)/100.0)
            for line in invoice.tax_line:
                #~ if not line.tax_id:
                    #~ raise osv.except_osv(_('Error de lectura!'), _('No se ha podido cargar el impuesto correctamente. Contacte con su administrador!'))
                if not line.tax_id.parent_id: #condicion agregada para que sume los totales de los impuestos padre
                    res[invoice.id]['amount_tax'] += line.amount
            res[invoice.id]['amount_total'] = res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed'] - res[invoice.id]['amount_discount']
        return res

    #~ def _get_invoice_line(self, cr, uid, ids, context=None):
        #~ result = {}
        #~ for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            #~ result[line.invoice_id.id] = True
        #~ return result.keys()
#~
    def _get_invoice_tax(self, cr, uid, ids, context=None):
        print "en _get_invoice_tax >>>>>>>>>>>>>>>>>>>>>>>"
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    #~ def split_invoice(self, cr, uid, ids, context=None):
        #~ """ Split the invoice when the lines exceed the maximum set for the company
        #~ """
        #~ res = {}
        #~ for inv in self.browse(cr, uid, ids):
            #~ order_id = False
            #~ len_lines = len(inv.invoice_line)
            #~ max_lines = inv.company_id.lines_invoice
            #~ if max_lines <= 1:
                #~ raise osv.except_osv(_('Error !'), _(u'Por favor configure la cantidad de lineas de factura en:\nConfiguracion->Compañias->Compañias->Configuracion'))
            #~ if inv.type not in ["out_invoice","out_refund"]:
                #~ continue
            #~ if len_lines > max_lines:
                #~ cr.execute('SELECT rel.order_id ' \
                #~ 'FROM sale_order_invoice_rel AS rel ' \
                #~ 'WHERE rel.invoice_id = %s limit 1' % inv.id)
                #~ result = cr.fetchone()
                #~ if result:
                    #~ order_id = result[0]
                #~ invoice = self.read(cr, uid, inv.id, ['name', 'type', 'number', 'origin', 'supplier_invoice_number', 'comment', 'date_due', 'partner_id',   'partner_contact', 'partner_insite', 'partner_ref', 'payment_term', 'account_id', 'currency_id', 'invoice_line', 'tax_line', 'journal_id', 'period_id', "user_id"])
                #~ invoice.update({
                    #~ 'state': 'draft',
                    #~ 'number': False,
                    #~ 'invoice_line': [],
                    #~ 'tax_line': [],
                #~ })
                #~ # take the id part of the tuple returned for many2one fields
                #~ invoice.pop('id', None)
                #~ for field in ( 'partner_id',
                        #~ 'account_id', 'currency_id', 'payment_term', 'journal_id', 'period_id','user_id'):
                    #~ invoice[field] = invoice[field] and invoice[field][0]
                #~ count = 1
                #~ inv_id = False
                #~ inv_split = []
                #~ inv_lines = inv.invoice_line
                #~ inv_count = len_lines - max_lines
                #~ for line in inv_lines:
                    #~ if count > inv_count:
                        #~ break
                    #~ if count % max_lines == 1:
                        #~ inv_id = self.create(cr, uid, invoice)
                        #~ cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order_id, inv_id))
                        #~ inv_split.append(inv_id)
                    #~ if inv_id:
                        #~ self.pool.get('account.invoice.line').write(cr,uid,line.id,{'invoice_id':inv_id})
                    #~ count += 1
                #~ res[inv.id] = inv_split
        #~
        #~ # recalculamos los montos de las facturas
        #~ for k in res.keys():
            #~ self.button_compute(cr, uid, [k], set_total=True)
            #~ for v in res[k]:
                #~ self.button_compute(cr, uid, [v], set_total=True)
        #~ return res
#~
    #~ def invoice_validate(self, cr, uid, ids, context=None):
        #~ for inv in self.browse(cr, uid, ids):
            #~ len_lines = len(inv.invoice_line)
            #~ max_lines = inv.company_id.lines_invoice
            #~ if inv.type not in ["out_invoice","out_refund"]:
                #~ continue
            #~ if len_lines > max_lines:
               #~ raise osv.except_osv(_('Acción Inválida!'), _(u'No puede validar una factura con mas de %d lineas, por favor divida la factura e intente nuevamente!'%max_lines))
        #~ return super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
    #~
    #~ def set_print_state(self, cr, uid, ids, context=None):
        #~ invoices = self.browse(cr, uid, ids, context=context)
        #~ res = {}
        #~ for invoice in invoices:
            #~ print_state = invoice.print_state=='draft' and 'printed' \
                        #~ or 'reprinted'
            #~ vals = {
                    #~ 'print_state': print_state,
                    #~ 'print_count': invoice.print_count + 1,
            #~ }
            #~ if print_state == 'printed':
                #~ vals.update({'print_uid':uid})
            #~ elif print_state == 'reprinted':
                #~ vals.update({'reprint_uid':uid})
            #~ res.update({invoice.id:print_state})
            #~ self.write(cr, uid, [invoice.id], vals, context=context)
        #~ return res
    #~
    #~ def reset_print_state(self, cr, uid, ids, context=None):
        #~ return self.write(cr, uid, ids, {'print_state':'draft'}, context=context)

    #~ _columns = {
        #~ 'discount': fields.float('Descuento en factura (%)', digits=(16, 4),readonly=True, states={'draft':[('readonly',False)]}, help="""Si
                                  #~ eliges aplicar un descuento este será aplicado
                                  #~ a la base imponible de la factura, es decir previo
                                  #~ a la aplicación del impuesto."""),
        #~ 'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
            #~ store={
                #~ 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                #~ 'account.invoice.tax': (_get_invoice_tax, None, 20),
                #~ 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            #~ },
            #~ multi='all'),
        #~ 'amount_discount': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Descuento',
            #~ store={
                #~ 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                #~ 'account.invoice.tax': (_get_invoice_tax, None, 20),
                #~ 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            #~ },
            #~ multi='all'),
        #~ 'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
            #~ store={
                #~ 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                #~ 'account.invoice.tax': (_get_invoice_tax, None, 20),
                #~ 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            #~ },
            #~ multi='all'),
        #~ 'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            #~ store={
                #~ 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                #~ 'account.invoice.tax': (_get_invoice_tax, None, 20),
                #~ 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            #~ },
            #~ multi='all'),
        #~ 'invoice_lot_id': fields.many2one('account.invoice.lot', "Lote de Facturas"),
        #~ 'print_state' : fields.selection([
                #~ ('draft','Lista para imprimir'),
                #~ ('printed','Impresa'),
                #~ ('reopen','Lista para reimprimir'),
                #~ ('reprinted', 'Reimpresa'),
                #~ ], required=True),
        #~ 'print_count' : fields.integer('Cantidad de impresiones', required=True),
        #~ 'print_uid' : fields.many2one('res.users','Imprimido por usuario'),
        #~ 'reprint_uid' : fields.many2one('res.users','Re-Imprimido por usuario'),
        #~ 'reception_date': fields.date('Fecha de Recepción',readonly=True, states={'draft':[('readonly',False)]}, help='Fecha de recepción del pedido que genero esta factura.'),
        #~ 'shop_id': fields.many2one('sale.shop', 'Oficina'),
    #~ }


    #~ def onchange_payment_term_date_invoice(self, cr, uid, ids, payment_term_id, date_invoice):
        #~ """ Herencia: esta funcion recalcula la fecha de vencimiento al pulsar el boton <validar> en la factura"""
        #~ vals = super(account_invoice, self).onchange_payment_term_date_invoice(cr, uid, ids, payment_term_id, date_invoice)
        #~ idn = type(ids) == int and [ids] or ids
        #~ if idn:
            #~ val = self.browse(cr,uid,idn[0])
            #~ pterm_list = self.pool.get('account.payment.term').compute(cr, uid, payment_term_id, value=1, date_ref=val.reception_date)
            #~ if pterm_list:
                #~ pterm_list = [line[0] for line in pterm_list]
                #~ pterm_list.sort()
                #~ date_due = pterm_list[-1]
                #~ vals['value'].update({'date_due':date_due })
        #~ return vals


    #~ _defaults = {
        #~ 'print_state': 'draft',
        #~ 'print_count': 0,
    #~ }
#~ account_invoice()


#~ class inherited_account_invoice_line(osv.osv):
    #~ _inherit = 'account.invoice.line'
    #~
   #~
    #~ # Herencia del onchange de productos de la linea de factura del proveedor
    #~ def product_id_change_inh(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None, measure=False):
        #~
        #~ if context is None:
            #~ context = {}
        #~ result = super(inherited_account_invoice_line,self).product_id_change(cr, uid, ids, product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id, context, company_id)
        #~ product_obj = self.pool.get('product.product')
        #~ product_brw = product_obj.browse(cr, uid, product, context=context)
        #~ result['value'].update({'measure': product_brw.measure_po or product_brw.measure})
        #~ return result
#~
#~
    #~
#~ inherited_account_invoice_line()

#~ class inherited_account_invoice_tax(osv.osv):
    #~ _inherit = "account.invoice.tax"
#~
    #~ def base_change(self, cr, uid, ids, base, currency_id=False, company_id=False, date_invoice=False):
        #~ return super(inherited_account_invoice_tax, self).base_change(cr, uid, ids, context=context)
#~
    #~ def amount_change(self, cr, uid, ids, amount, currency_id=False, company_id=False, date_invoice=False):
        #~ return super(inherited_account_invoice_tax, self).amount_change(cr, uid, ids, context=context)
    #~
    #~ # reemplazada funcion branch vauxoo que a su vez reemplaza la original
    #~ # fuente: (vauxoo/account_invoice_tax/account_invoice_tax.py: line 68)
    #~ def compute(self, cr, uid, invoice_id, context=None):#method overriding
        #~ tax_grouped = {}
        #~ tax_obj = self.pool.get('account.tax')
        #~ cur_obj = self.pool.get('res.currency')
        #~ inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        #~ cur = inv.currency_id
        #~ company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        #~ for line in inv.invoice_line:
            #~ # se modifican las siguientes dos lineas para adaptar que el
            #~ # impuesto se calcule al deducir el descuento del monto base
            #~ dsc1 = (1.0 - inv.discount/100.0) # factor de descuento
            #~ # price_unit = line.price_unit * factor de descuento
            #~ for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* dsc1), line.quantity, line.product_id, inv.partner_id)['taxes']:
                #~ val={}
                #~ val['invoice_id'] = inv.id
                #~ val['name'] = tax['name']
                #~ val['amount'] = tax['amount']
                #~ val['manual'] = False
                #~ val['sequence'] = tax['sequence']
                #~ val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])
                #~ #start custom change (vauxoo)
                #~ val['tax_id'] = tax['id']
                #~ #end custom change (vauxoo)
#~
                #~ if inv.type in ('out_invoice','in_invoice'):
                    #~ val['base_code_id'] = tax['base_code_id']
                    #~ val['tax_code_id'] = tax['tax_code_id']
                    #~ val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    #~ val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    #~ val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    #~ val['account_analytic_id'] = tax['account_analytic_collected_id']
                #~ else:
                    #~ val['base_code_id'] = tax['ref_base_code_id']
                    #~ val['tax_code_id'] = tax['ref_tax_code_id']
                    #~ val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    #~ val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    #~ val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    #~ val['account_analytic_id'] = tax['account_analytic_paid_id']
                #~ #start custom change (vauxoo)
                #~ #key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                #~ key = (val['tax_id'])
                #~ #end custom change (vauxoo)
                #~ if not key in tax_grouped:
                    #~ tax_grouped[key] = val
                #~ else:
                    #~ tax_grouped[key]['amount'] += val['amount']
                    #~ tax_grouped[key]['base'] += val['base']
                    #~ tax_grouped[key]['base_amount'] += val['base_amount']
                    #~ tax_grouped[key]['tax_amount'] += val['tax_amount']
#~
        #~ for t in tax_grouped.values():
            #~ t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            #~ t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            #~ t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            #~ t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        #~ return tax_grouped
#~
#~ inherited_account_invoice_line()
