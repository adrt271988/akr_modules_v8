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
#    it under akr terms of akr GNU Affero General Public License as published by
#    akr Free Software Foundation, eiakrr version 3 of akr License, or
#    (at your option) any later version.
#
#    This program is distributed in akr hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even akr implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See akr
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of akr GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import time
from openerp.report import report_sxw
import math

class picking_kasa(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_kasa, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_calc_pack': self._get_calc_pack,
            'get_total_qty': self._get_total_qty,
            'get_total_qty_pack': self._get_total_qty_pack,
            'get_total_volumen_pack': self._get_total_volumen_pack,
            'get_total_weight_pack': self._get_total_weight_pack,
        })
        self.total_qty = 0.0
        self.total_qty_pack = 0.0
        self.total_volumen_pack = 0.0
        self.total_weight_pack = 0.0

    def _get_calc_pack(self, product, quantity, tipo):
        prod_ul = self.pool.get('product.ul')
        prod_pack = self.pool.get('product.packaging')

        dict_pack = {
            'qty_pack': 0.0,
            'vol_pack': 0.0,
            'wei_pack': 0.0
        }
        if product.packaging_ids:
            ul_id = prod_ul.search(self.cr, self.uid, [('name', 'like', 'BULTO')])
            if ul_id:
                ul_id = ul_id[0]
                pack_id = prod_pack.search(self.cr, self.uid, [('product_tmpl_id', '=', product.id),('ul', '=', ul_id)])
                if pack_id:
                    pack_id = pack_id[0]
                    pack_brw = prod_pack.browse(self.cr, self.uid, pack_id)
                    if pack_brw.qty > 0.001:
                        dict_pack['qty_pack'] = math.ceil(quantity/pack_brw.qty)
                        dict_pack['vol_pack'] = dict_pack['qty_pack'] * ((product.volume or 0.0) * pack_brw.qty)
                        dict_pack['wei_pack'] = dict_pack['qty_pack'] * (product.weight * pack_brw.qty)
                    else:
                        dict_pack['qty_pack'] = quantity
                        dict_pack['vol_pack'] = ((product.volume or 0.0) * quantity)
                        dict_pack['wei_pack'] = ((product.weight or 0.0) * quantity)
                else:
                    dict_pack['qty_pack'] = quantity
                    dict_pack['vol_pack'] = ((product.volume or 0.0) * quantity)
                    dict_pack['wei_pack'] = ((product.weight or 0.0) * quantity)
            else:
                dict_pack['qty_pack'] = quantity
                dict_pack['vol_pack'] = ((product.volume or 0.0) * quantity)
                dict_pack['wei_pack'] = ((product.weight or 0.0) * quantity)
        else:
            dict_pack['qty_pack'] = quantity
            dict_pack['vol_pack'] = ((product.volume or 0.0) * quantity)
            dict_pack['wei_pack'] = ((product.weight or 0.0) * quantity)

        if tipo == 'qty_pack':
            self.total_qty += quantity
            self.total_qty_pack += dict_pack['qty_pack']
        elif tipo == 'vol_pack':
            self.total_volumen_pack += dict_pack['vol_pack']
        elif tipo == 'wei_pack':
            self.total_weight_pack += dict_pack['wei_pack']

        return dict_pack[tipo]


    def _get_total_qty(self):
        return self.total_qty


    def _get_total_qty_pack(self):
        return self.total_qty_pack


    def _get_total_volumen_pack(self):
        return self.total_volumen_pack


    def _get_total_weight_pack(self):
        return self.total_weight_pack


for suffix in ['', '.in', '.out']:
    report_sxw.report_sxw('report.kasa.stock.picking.list' + suffix,
                          'stock.picking' + suffix,
                          'kasa_stock/report/kasa_packing_list.rml',
                          parser=picking_kasa)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
