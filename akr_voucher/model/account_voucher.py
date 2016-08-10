# -*- encoding: utf-8 -*-
import time
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
from openerp.report import report_sxw
import openerp

class account_voucher(osv.osv):

    _inherit = 'account.voucher'
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        res = super(account_voucher,self).recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)

        move_obj = self.pool.get('account.move.line')
        invo_obj = self.pool.get('account.invoice')

        for i in res['value']['line_dr_ids']:
            print i
            move_id = move_obj.browse(cr, uid, i['move_line_id']).move_id
            if move_id:
                invo_id = invo_obj.search(cr, uid, [('move_id', '=', move_id.id)])
                inv_brw = invo_obj.browse(cr, uid, invo_id)
                if inv_brw.islr_wh_doc_id:
                    i.update({'amount_wh_islr': inv_brw.islr_wh_doc_id.amount_total_ret, 'amount_unreconciled': i['amount_unreconciled']-inv_brw.islr_wh_doc_id.amount_total_ret })
                for j in inv_brw.tax_line:
                    if j.tax_id.ret:
                        i.update({'amount_wh_iva': j.amount,'amount_unreconciled': i['amount_unreconciled']-j.amount})

        for k in res['value']['line_cr_ids']:

            move_id = move_obj.browse(cr, uid, k['move_line_id']).move_id
            if move_id:
                invo_id = invo_obj.search(cr, uid, [('move_id', '=', move_id.id)])
                inv_brw = invo_obj.browse(cr, uid, invo_id)
                if inv_brw.islr_wh_doc_id:
                    k.update({'amount_wh_islr': inv_brw.islr_wh_doc_id.amount_total_ret, 'amount_unreconciled': k['amount_unreconciled']-inv_brw.islr_wh_doc_id.amount_total_ret })
                for r in inv_brw.tax_line:
                    if r.tax_id.ret:
                        k.update({'amount_wh_iva': r.amount, 'amount_unreconciled': k['amount_unreconciled']-r.amount })
        return res

    _columns = {
                'date_pay':fields.date('Fecha de pago',
                           help="Fecha en que entró el dinero en cuenta", copy=False),
                'pay_method':fields.selection([('E','Efectivo'),('C','Cheque'),('D','Depósito'),('T','Transferencia')], 'Forma de Pago'),
                 }

account_voucher()


class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'


    _columns = {
                'amount_wh_iva':fields.float('Ret. IVA', digits_compute=dp.get_precision('Account')),
                'amount_wh_islr':fields.float('Ret. ISLR', digits_compute=dp.get_precision('Account')),
}

account_voucher_line()
