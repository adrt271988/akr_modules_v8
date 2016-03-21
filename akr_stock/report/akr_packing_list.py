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
import math

class picking_akr(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_akr, self).__init__(cr, uid, name, context=context)
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
        if product.packaging_ids and tipo == 'qty_pack':
            qty_uds = quantity
            qty_x_bulto = [ pack.qty for pack in product.packaging_ids if pack.ul.name == 'BULTO']
            qty_x_caja = [ pack.qty for pack in product.packaging_ids if pack.ul.name == 'CAJA']

            if qty_x_bulto and qty_x_caja:
                if qty_uds%qty_x_bulto[0] == 0:
                    val = qty_uds/qty_x_bulto[0]
                else:
                    val = int(qty_uds/qty_x_bulto[0])+((qty_uds%qty_x_bulto[0])/qty_x_caja[0])

            elif not qty_x_caja and qty_x_bulto:
                val = qty_uds/qty_x_bulto[0]

            elif not qty_x_bulto and qty_x_caja:
                val = qty_uds/qty_x_caja[0]
            else:
                val= 0

            if val > 0:
                dict_pack['qty_pack'] = val  #math.ceil(quantity/pack_brw.qty)
                dict_pack['vol_pack'] = product.volume * quantity
                dict_pack['wei_pack'] = product.weight * quantity
            else:
                dict_pack['qty_pack'] = quantity
                dict_pack['vol_pack'] = product.volume * quantity
                dict_pack['wei_pack'] = product.weight * quantity
        else:
            dict_pack['qty_pack'] = quantity
            dict_pack['vol_pack'] = product.volume * quantity
            dict_pack['wei_pack'] = product.weight * quantity

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
    report_sxw.report_sxw('report.akr.stock.picking.list' + suffix,
                          'stock.picking' + suffix,
                          'akr_stock/report/akr_packing_list.rml',
                          parser=picking_akr)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
            #~
            #~ for pack in product.packaging_ids:
                #~
                #~ if pack.ul.name == 'BULTO':
                    #~ qty_x_bulto = pack.qty and pack.qty or 0.00
                    #~ while qty_uds >= qty_x_bulto:
                        #~ qty_uds = qty_uds - qty_x_bulto
                        #~ cont = cont + 1
                #~ print '--------',qty_uds
                #~ if pack.ul.name == 'CAJA':
                    #~ qty_x_caja = pack.qty and pack.qty or 0.00
                    #~ while qty_uds >= qty_x_caja:
                        #~ print '--------',qty_uds
                        #~ qty_uds = qty_uds - qty_x_caja
                        #~ cont = cont + 1
                    #~ print '--------',qty_uds
