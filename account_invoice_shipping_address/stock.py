# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#    Author: Nicola Malcontenti <nicola.malcontenti@agilebg.com>
#
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
#
##############################################################################

from openerp.osv import orm


class StockPicking(orm.Model):
    _inherit = "stock.picking"

    #def _get_invoice_vals(self, cr, uid, key, inv_type,
    #                      journal_id, origin, context=None):
    #    invoice_vals = super(StockPicking, self)._get_invoice_vals(
    #        cr, uid, key, inv_type, journal_id, origin, context=context)
    #    if context.get('active_id'):
    #        picking_id = int(context['active_id'])
    #        partner_id = self.browse(cr, uid, picking_id, context=context).partner_id
    #        if partner_id:
    #            invoice_vals['address_shipping_id'] = partner_id.id
    #    return invoice_vals

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, origin, context=None):
        if context is None:
            context = {}
        partner, currency_id, company_id, user_id = key
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        return {
            'origin': origin and origin.picking_id.name or origin,
            'date_invoice': context.get('date_inv', False),
            'address_shipping_id': partner.id,
            'user_id': user_id,
            'partner_id': partner.id,
            'account_id': account_id,
            'payment_term': payment_term,
            'type': inv_type,
            'fiscal_position': partner.property_account_position.id,
            'company_id': company_id,
            'currency_id': currency_id,
            'journal_id': journal_id,
        }
