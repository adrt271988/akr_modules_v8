#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Edgar Rivero (edgarrivero@gmail.com).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Edgar Rivero
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import time
from openerp.report import report_sxw

class invoice_akr(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(invoice_akr, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_sale_id': self.get_sale_id,
            'calc_total': self.calc_total,
            'freight_get': self.freight_get,
            'get_sub_total': self.get_sub_total,
            'get_total_invoice': self.get_total_invoice,
            'get_total_insurance': self.get_total_insurance,
            'get_order_origin': self.get_order_origin,
        })
        self.total = 0.0
        self.sub_total = 0.0
        self.freight = 0.0
        self.insurance = 0.0


    def product_carrier(self, product_id):
        carrier = self.pool.get('delivery.carrier')
        if product_id:
            if carrier.search(self.cr, self.uid, [('product_id', '=', product_id.id)]):
                return True
        return False


    def calc_total(self, invoice):
        prod_obj = self.pool.get('product.product')
        seguro = prod_obj.search(self.cr, self.uid, [('default_code', '=', '0000')])
        if seguro:
            seguro = seguro[0]

        total_f = 0.0
        total_i = 0.0
        for line in invoice.invoice_line:
            if self.product_carrier(line.product_id):
                total_f += line.price_subtotal
            elif line.product_id:
                if line.product_id.id == seguro:
                    total_i += line.price_subtotal

        self.sub_total = ((invoice.amount_untaxed - total_f) - total_i)
        self.total = invoice.amount_total
        self.freight = total_f
        self.insurance = total_i


    def freight_get(self, invoice):
        return self.freight


    def get_sub_total(self, invoice):
        return self.sub_total


    def get_total_invoice(self, invoice):
        return self.total


    def get_total_insurance(self, invoice):
        return self.insurance


    def get_sale_id(self, invoice):
        sale_obj = self.pool.get("sale.order")
        move_obj = self.pool.get("stock.picking")
        sale_id = sale_obj.search(self.cr, self. uid, [('name', '=', invoice.origin)])

        if not sale_id:
            picking_id = move_obj.search(self.cr, self. uid, [('name', '=', invoice.origin)])
            picking_brw = move_obj.browse(self.cr, self.uid, picking_id[0])
            sale_id = sale_obj.search(self.cr, self. uid, [('name', '=', picking_brw.origin)])

        if sale_id:
            sale_brw = sale_obj.browse(self.cr, self.uid, sale_id[0])
            street = sale_brw.partner_shipping_id and sale_brw.partner_shipping_id.street or ''
            street += sale_brw.partner_shipping_id and sale_brw.partner_shipping_id.street2 or ''
            vat = sale_brw.partner_shipping_id and sale_brw.partner_shipping_id.vat and sale_brw.partner_shipping_id.vat[2:] or ''
            dict_sale = {
                'name': sale_brw.partner_shipping_id and sale_brw.partner_shipping_id.name or '',
                'vat': vat,
                'street': street,
                'phone': sale_brw.partner_shipping_id and sale_brw.partner_shipping_id.phone or '',
                'email': sale_brw.partner_shipping_id and sale_brw.partner_shipping_id.email or '',
                'port_loading': sale_brw.port_loading and sale_brw.port_loading or '',
                'final_destination': sale_brw.partner_shipping_id and sale_brw.partner_shipping_id.fax or '',
                'terms_delivery': sale_brw.incoterm and sale_brw.incoterm.name or '',
                'cbm': sale_brw.cbm and sale_brw.cbm or '0.00',
                'wtotal': sale_brw.wtotal and sale_brw.wtotal or '0.00',
            }
            sale_info = dict_sale
        else:
            sale_info = {
                'name': '',
                'vat': '',
                'street': '',
                'phone': '',
                'email': '',
                'port_loading': '',
                'final_destination': '',
                'terms_delivery': '',
                'cbm': '',
                'wtotal': '',
            }

        return sale_info

    def get_order_origin(self, invoice):
        sale_obj = self.pool.get("sale.order")
        move_obj = self.pool.get("stock.picking")
        order = ''
        if invoice.type == 'out_invoice':
            picking_id = move_obj.search(self.cr, self. uid, [('name', '=', invoice.origin)])
            picking_brw = move_obj.browse(self.cr, self.uid, picking_id[0])
            sale_id = sale_obj.search(self.cr, self. uid, [('name', '=', picking_brw.origin)])
            sale_brw = sale_obj.browse(self.cr, self.uid, sale_id[0])
            order = sale_brw.name
        elif invoice.type == 'in_invoice':
            order = invoice.name
        else:
            order = invoice.reference
        return order

report_sxw.report_sxw(
    'report.akr.account.invoice',
    'account.invoice',
    'akr_invoice/report/invoice_akr.rml',
    parser=invoice_akr
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
