# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from datetime import datetime
# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale_refund',
    'in_refund': 'purchase_refund',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Supplier Invoice
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Supplier Refund
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line if not line.tax_id.ret)
        self.amount_total = self.amount_untaxed + self.amount_tax

    @api.multi
    def button_reset_taxes(self):
        account_tax = self.env['account.tax']
        account_invoice_tax = self.env['account.invoice.tax']
        ctx = dict(self._context)
        for invoice in self:
            self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
            self.invalidate_cache()
            partner = invoice.partner_id
            amount_iva = importe = 0
            if partner.lang:
                ctx['lang'] = partner.lang
            for aux in account_invoice_tax.compute(invoice.with_context(ctx)).values():
                tax_brw = account_tax.browse(aux['tax_id'])
                if 'IVA' in tax_brw.name and not tax_brw.ret:
                    amount_iva = aux['amount']
            print 'amount',amount_iva

            for taxe in account_invoice_tax.compute(invoice.with_context(ctx)).values():
                taxe_brw = account_tax.browse(taxe['tax_id'])
                if taxe_brw.ret:
                    print 'en la movida'
                    taxe['base']=taxe['base_amount']=amount_iva
                    taxe['tax_amount']=taxe['amount']=taxe_brw.amount*amount_iva
                account_invoice_tax.create(taxe)
        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'invoice_line': []})

    @api.multi
    def action_move_create(self):
        '''Metodo heredado para realizar la creacion del comprobante de retencion del proveedor al validar la factura. '''
        res = super(account_invoice, self).action_move_create()

        apply_wh = False
        for tax in self.tax_line:
            if tax.tax_id.ret:
                apply_wh = True

        if apply_wh:
            date_inv = datetime.strptime(self.date_invoice, "%Y-%m-%d")
            date_doc = datetime.strptime(self.date_document, "%Y-%m-%d")

            query = ''' select  MAX(number) FROM account_wh_iva '''
            self._cr.execute(query)
            val = self._cr.fetchone()
            value = val and val[0] or (date_inv.strftime('%Y%m')+'0' or date_doc.strftime('%Y%m')+'0')
            code = str(date_inv.strftime('%Y%m') or date_doc.strftime('%Y%m'))+str(int(value[6:])+1).zfill(8)
            account_invoice_tax = self.env['account.invoice.tax']
            account_wh_iva = self.env['account.wh.iva']
            wh_iva_val = False

            #validamos que el documento sea factura de compra o N/C-N/D de proveedor y que no posea exclusion de retencion
            if self.type not in ('out_invoice', 'out_refund')  and self.journal_id.type in ('purchase','purchase_refund','purchase_debit') and not self.vat_apply:

                if self.consolidate_vat_wh: #Agrupar facturas en un comprobante diario
                    #verificamos si ya existe un comprobante generado para el proveedor con la fecha en curso
                    wh_iva_val = account_wh_iva.search([('partner_id','=',self.partner_id.id),('date_ret','=',datetime.now().strftime('%Y-%m-%d'))])
                if self.tax_line: # verificamos si el documento tiene impuestos
                    base = 0
                    ret = 0
                    for i in self.tax_line:
                        number = self.nro_ctrl
                        #if not i.tax_id.ret:
                        if i.tax_id.ret:
                            print '*****',i.name
                            #base = i.base
                            base = self.amount_total
                            #ret = i.amount
                            ret = i.base
                            name = i.name
                            inv_tax_id = i.id
                            account = self.type == 'in_invoice' and i.tax_id.wh_vat_collected_account_id.id or self.type == 'in_refund' and i.tax_id.wh_vat_paid_account_id.id or i.tax_id.account_collected_id.id
                            lines = {
                                        'inv_tax_id': inv_tax_id,
                                        'base': base,
                                        'amount': ret,
                                      }
                            details = {
                                        'name': name,
                                        'move_id': self.move_id.id,
                                        'invoice_id': self.id,
                                        'amount_ret': ret,
                                        'supplier_invoice_number': number,
                                        'tax_line': [(0,0,lines)]
                                      }
                            vals_wh = {
                                'partner_id': self.partner_id.id,
                                'period_id': self.period_id.id,
                                'journal_id': self.journal_id.id,
                                'account_id': account,
                                'fortnight':int(date_inv.strftime('%d') or date_doc.strftime('%d')) >= 15 and 'True' or 'False',
                                'date_ret': date_inv or date_doc,
                                'number':code,
                                'name': 'Retencion IVA '+str(self.partner_id.name),
                                'code': code[6:],
                                'date': date_inv or date_doc,
                                'amount_base_ret': base,
                                'type': self.type,
                                'total_tax_ret': ret,
                                'wh_lines': [(0,0,details)]
                                }

                            if wh_iva_val:
                                account_wh_iva.wh_iva_val.write({ 'wh_lines': [(0,0,details)] })
                            else:
                                wh_id = account_wh_iva.create(vals_wh)
                                print '..........',wh_id.id
                                self.write({'wh_iva_id': wh_id.id })
                                #self.[id].write({'})


    @api.multi
    def compute_invoice_totals(self, company_currency, ref, invoice_move_lines):
        '''Herencia: Funcion que calcula los totales de la factura. (se le agrego una condicion para que
                     sume solo los montos de los impuestos padre, es decir, no totalice retenciones)'''
        total = 0
        total_currency = 0
        for line in invoice_move_lines:

            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(date=self.date_invoice or fields.Date.context_today(self))
                line['currency_id'] = currency.id
                line['amount_currency'] = currency.round(line['price'])
                line['price'] = currency.compute(line['price'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])
            line['ref'] = ref
            if self.type in ('out_invoice','in_refund'):
                total += line['price']
                total_currency += line['amount_currency'] or line['price']
                line['price'] = - line['price']
            else:
                #condicion agregada
                if line['type'] == 'tax' and line['price']>0 and ('RETENCION' in line['name'].upper() or u'RETENCIÓN' in line['name'].upper()):
                    line.update({'price': line['price']*-1})
                total -= line['price']
                total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, invoice_move_lines

#         date_invoice = inv.date_invoice

            # check if taxes are all computed
 #           compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
  #          inv.check_tax_lines(compute_taxes)



            #~ if inv.type in ('in_invoice', 'in_refund'):
                #~ ref = inv.reference
            #~ else:
                #~ ref = inv.number
#~
            #~ diff_currency = inv.currency_id != company_currency
            #~ # create one move line for the total and possibly adjust the other lines amount
            #~ total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)
#~
            #~ name = inv.supplier_invoice_number or inv.name or '/'
            #~ totlines = []
            #~ if inv.payment_term:
                #~ totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            #~ if totlines:
                #~ res_amount_currency = total_currency
                #~ ctx['date'] = date_invoice
                #~ for i, t in enumerate(totlines):
                    #~ if inv.currency_id != company_currency:
                        #~ amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    #~ else:
                        #~ amount_currency = False
#~
                    #~ # last line: add the diff
                    #~ res_amount_currency -= amount_currency or 0
                    #~ if i + 1 == len(totlines):
                        #~ amount_currency += res_amount_currency
#~
                    #~ iml.append({
                        #~ 'type': 'dest',
                        #~ 'name': name,
                        #~ 'price': t[1],
                        #~ 'account_id': inv.account_id.id,
                        #~ 'date_maturity': t[0],
                        #~ 'amount_currency': diff_currency and amount_currency,
                        #~ 'currency_id': diff_currency and inv.currency_id.id,
                        #~ 'ref': ref,
                    #~ })
            #~ else:
                #~ iml.append({
                    #~ 'type': 'dest',
                    #~ 'name': name,
                    #~ 'price': total,
                    #~ 'account_id': inv.account_id.id,
                    #~ 'date_maturity': inv.date_due,
                    #~ 'amount_currency': diff_currency and total_currency,
                    #~ 'currency_id': diff_currency and inv.currency_id.id,
                    #~ 'ref': ref
                #~ })
#~
            #~ date = date_invoice

            #part = self.env['res.partner']._find_accounting_partner(inv.partner_id)

           # line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            #line = inv.group_lines(iml, line)

#        return res
