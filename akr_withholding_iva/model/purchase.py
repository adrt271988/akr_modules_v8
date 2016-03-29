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

from openerp.osv import fields,osv
from openerp.tools.translate import _


class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'

    def onchange_product_id(self,cr, uid, ids, pricelist, product, qty, uom,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
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
