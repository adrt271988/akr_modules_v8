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

import pytz
from openerp import SUPERUSER_ID, workflow
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import attrgetter
from openerp.tools.safe_eval import safe_eval as eval
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv.orm import browse_record_list, browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools.float_utils import float_compare



class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    def _calc_line_base_price(self, cr, uid, line, context=None):
        """Return the base price of the line to be used for tax calculation.

        This function can be extended by other modules to modify this base
        price (adding a discount, for example).
        """
        return line.price_unit

    def _calc_line_quantity(self, cr, uid, line, context=None):
        """Return the base quantity of the line to be used for the subtotal.

        This function can be extended by other modules to modify this base
        quantity (adding for example offers 3x2 and so on).
        """
        return line.product_qty

    def onchange_product_id(self,cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
        '''Funcion heredada para realizar la carga automatica del impuesto "Retencion"
            en las lineas del pedido'''
        tax = []
        result =  super(purchase_order_line, self).onchange_product_id(cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned, name=name, price_unit=price_unit, state=state, context=context)
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context)

        if result['value'].get('taxes_id'):
            tax = result['value'].get('taxes_id')

        if partner.partner_wh_tax_id:
            tax.append(partner.partner_wh_tax_id.id)
            result['value'].update({'taxes_id':tax})

        return result

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):   #This code is not working and ,is this calculation is crct?
        ''' Funcion heredada para el recalculo de el monto de impuestos y total, según cambios efectuados
            para la generacion de los comprobantes de retención de IVA.'''

        res = super(purchase_order, self)._amount_all(cr, uid, ids, field_name, arg, context)

        cur_obj=self.pool.get('res.currency')
        line_obj = self.pool['purchase.order.line']
        for order in self.browse(cr, uid, ids, context=context):
            val =  0.0
            tax_obj = self.pool['account.tax']
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                line_price = line_obj._calc_line_base_price(cr, uid, line, context=context)
                line_qty = line_obj._calc_line_quantity(cr, uid, line, context=context)
                for i in line.taxes_id:
                    if not i.ret:
                        taxes = tax_obj.browse(cr, uid, i.id)
                for c in tax_obj.compute_all(cr, uid, taxes, line_price, line_qty, line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):

        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {

        'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The total amount"),

    }
