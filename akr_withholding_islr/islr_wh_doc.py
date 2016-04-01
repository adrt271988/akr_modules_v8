# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Humberto Arocha           <hbto@vauxoo.com>
#              Maria Gabriela Quilarque  <gabriela@vauxoo.com>
#              Javier Duran              <javier@vauxoo.com>
#              Yanina Aular              <yanina.aular@vauxoo.com>
#    Planified by: Nhomar Hernandez <nhomar@vauxoo.com>
#    Finance by: Helados Gilda, C.A. http://heladosgilda.com.ve
#    Audited by: Humberto Arocha hbto@vauxoo.com
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################
import time

from openerp import api
from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _

class AkrIslrWhDocInvoices(osv.osv):
    _inherit = "islr.wh.doc.invoices"

    def _get_wh(self, cr, uid, ids, concept_id, context=None):
        """ Return a dictionary containing all the values of the retention of an
        invoice line.
        @param concept_id: Withholding reason
        """
        # TODO: Change the signature of this method
        # This record already has the concept_id built-in
        context = context or {}
        ids = isinstance(ids, (int, long)) and [ids] or ids
        ixwl_obj = self.pool.get('islr.xml.wh.line')
        iwdl_obj = self.pool.get('islr.wh.doc.line')
        iwdl_brw = iwdl_obj.browse(cr, uid, ids[0], context=context)

        ut_date = iwdl_brw.islr_wh_doc_id.date_uid
        ut_obj = self.pool.get('l10n.ut')
        money2ut = ut_obj.compute
        ut2money = ut_obj.compute_ut_to_money

        vendor, buyer, wh_agent = self._get_partners(
            cr, uid, iwdl_brw.invoice_id)
        wh_agent = wh_agent
        apply_income = not vendor.islr_exempt
        residence = self._get_residence(cr, uid, vendor, buyer)
        nature = self._get_nature(cr, uid, vendor)

        concept_id = iwdl_brw.concept_id.id
        # rate_base,rate_minimum,rate_wh_perc,rate_subtract,rate_code,rate_id,
        # rate_name
        # Add a Key in context to store date of ret fot U.T. value
        # determination
        # TODO: Future me, this context update need to be checked with the
        # other date in the withholding in order to take into account the
        # customer income withholding.
        context.update({
            'wh_islr_date_ret':
            iwdl_brw.islr_wh_doc_id.date_uid or
            iwdl_brw.islr_wh_doc_id.date_ret or False
        })
        base = 0
        wh_concept = 0.0
        amount_not_wh = sum([x.price_subtotal for x in iwdl_brw.invoice_id.invoice_line if (x.concept_id.withholdable is False)])

        # Using a clousure to make this call shorter
        f_xc = ut_obj.sxc(
            cr, uid, iwdl_brw.invoice_id.currency_id.id,
            iwdl_brw.invoice_id.company_id.currency_id.id,
            iwdl_brw.invoice_id.date_invoice)
        if iwdl_brw.invoice_id.type in ('in_invoice', 'in_refund'):
            for line in iwdl_brw.xml_ids:
                base += f_xc(line.account_invoice_line_id.price_subtotal)

            # rate_base, rate_minimum, rate_wh_perc, rate_subtract, rate_code,
            # rate_id, rate_name, rate2 = self._get_rate(
            #    cr, uid, ail_brw.concept_id.id, residence, nature, base=base,
            #    inv_brw=ail_brw.invoice_id, context=context)
            rate_tuple = self._get_rate(
                cr, uid, concept_id, residence, nature, base=base,
                inv_brw=iwdl_brw.invoice_id, context=context)

            if rate_tuple[7]:
                apply_income = True
                residual_ut = (
                    (rate_tuple[0] / 100.0) * (rate_tuple[2] / 100.0) *
                    rate_tuple[7]['cumulative_base_ut'])
                residual_ut -= rate_tuple[7]['cumulative_tax_ut']
                residual_ut -= rate_tuple[7]['subtrahend']
            else:
                apply_income = (apply_income and
                                base >= rate_tuple[0] * rate_tuple[1] / 100.0)
            wh = 0.0
            subtract = apply_income and rate_tuple[3] or 0.0
            subtract_write = 0.0
            sb_concept = subtract
            for line in iwdl_brw.xml_ids:
                base_line = f_xc(line.account_invoice_line_id.price_subtotal)
                base_line_ut = money2ut(cr, uid, base_line, ut_date)
                values = {}
                if apply_income and not rate_tuple[7]:
                    wh_calc = ((rate_tuple[0] / 100.0) *
                               (rate_tuple[2] / 100.0) * base_line)
                    if subtract >= wh_calc:
                        wh = 0.0
                        subtract -= wh_calc
                    else:
                        wh = wh_calc - subtract
                        subtract_write = subtract
                        subtract = 0.0
                    values = {
                        'wh': wh,
                        'raw_tax_ut': money2ut(cr, uid, wh, ut_date),
                        'sustract': subtract or subtract_write,
                    }
                elif apply_income and rate_tuple[7]:
                    tax_line_ut = (base_line_ut * (rate_tuple[0] / 100.0) *
                                   (rate_tuple[2] / 100.0))
                    if residual_ut >= tax_line_ut:
                        wh_ut = 0.0
                        residual_ut -= tax_line_ut
                    else:
                        wh_ut = tax_line_ut + residual_ut
                        subtract_write_ut = residual_ut
                        residual_ut = 0.0
                    wh = ut2money(cr, uid, wh_ut, ut_date)
                    values = {
                        'wh': wh,
                        'raw_tax_ut': wh_ut,
                        'sustract': ut2money(
                            cr, uid, residual_ut or subtract_write_ut,
                            ut_date),
                    }
                values.update({
                    'base': base_line * (rate_tuple[0] / 100.0),
                    'raw_base_ut': base_line_ut,
                    'rate_id': rate_tuple[5],
                    'porcent_rete': rate_tuple[2],
                    'concept_code': rate_tuple[4],
                })
                ixwl_obj.write(cr, uid, line.id, values, context=context)
                wh_concept += wh
        else:
            for line in iwdl_brw.invoice_id.invoice_line:
                if line.concept_id.id == concept_id:
                    base += f_xc(line.price_subtotal)
            
            rate_tuple = self._get_rate(
                cr, uid, concept_id, residence, nature, base=0.0,
                inv_brw=iwdl_brw.invoice_id, context=context)

            if rate_tuple[7]:
                apply_income = True
            else:
                apply_income = (apply_income and
                                base >= rate_tuple[0] * rate_tuple[1] / 100.0)
            sb_concept = apply_income and rate_tuple[3] or 0.0
            if apply_income:
                wh_concept = ((rate_tuple[0] / 100.0) *
                              rate_tuple[2] * base / 100.0)
                wh_concept -= sb_concept
        values = {
            'amount': wh_concept,
            'raw_tax_ut': money2ut(cr, uid, wh_concept, ut_date),
            'subtract': sb_concept,
            'base_amount': base * (rate_tuple[0] / 100.0),
            'raw_base_ut': money2ut(cr, uid, base, ut_date),
            'retencion_islr': rate_tuple[2],
            'islr_rates_id': rate_tuple[5],
            'amount_without_withholding': amount_not_wh,
        }
        iwdl_obj.write(cr, uid, ids[0], values, context=context)
        return True
        
class AkrIslrWhDocLine(osv.osv):
    _inherit = "islr.wh.doc.line"

    def _get_supplier_invoice_number(self, cr, uid, ids, fieldname, args, context=None):
        res = {}
        for iwdl_brw in self.browse(cr, uid, ids, context):
            if iwdl_brw.invoice_id:
                res[iwdl_brw.id] = iwdl_brw.invoice_id.supplier_invoice_number
        return res
    
    _columns = {
            'amount_without_withholding': fields.float('Monto Exento', digits=(16,2), help="Monto exento de retención ISLR"),
            'supplier_invoice_number': fields.function(_get_supplier_invoice_number, type='char',
                                        store=True, string='Factura de Proveedor', help="Factura de Proveedor"),
    }

