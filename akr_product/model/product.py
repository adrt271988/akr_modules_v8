#!/usr/bin/python
#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Edgar Rivero (ltorres134@gmail.com).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Luis Torres
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

import math
import re
import time

from openerp import tools
from openerp.osv import osv, fields, expression
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round


class product_template(osv.osv):

    _inherit = 'product.template'

    # precarga valores por defecto
    #~ def default_get(self, cr, uid, fields_list, context=None):
        #~ context = context and context or {}
        #~ res = super(product_template, self).default_get(cr, uid, fields_list, context)
        #~ account = self.pool.get('account.account').search(cr, uid, [('code', '=', '151.01')])
        #~ account_id = account and account[0] or ''
        #~ res.update({'valuation':'real_time','property_stock_account_input': account_id,'property_stock_account_output': account_id })
        #~ return res

    def _product_reserved(self, cr, uid, ids, field_names=None, arg=False, context=None):
        context = context or {}
        field_names = field_names or []
        return {}

    _columns = {
        'ref_2': fields.char('Reference Second', size=32),
        'brand': fields.char('Brand', size=64),
        'description_2': fields.char('Country of Origin', size=16),
        'arancel_cod': fields.char('Arancel Code', size=32),
        'moq': fields.char('Individual Packing', size=32),
        'landed_cost': fields.float('Landed Cost', digits_compute=dp.get_precision('Product Price')),
        #'landed_cost_cn': fields.float('Landed Cost CN', digits_compute=dp.get_precision('Product Price')),
   }
    _defaults = {
        'valuation': 'real_time',
            }

product_template()

class product_product(osv.osv):

    _inherit = 'product.product'
    _sql_constraints = [
                        ('default_code_uniq', 'unique(default_code)', 'Internal Reference must be unique per product!'),
                        ('default_ean13_bar', 'unique(ean13)', 'EAN13 Barcode must be unique per product!'),
                        ]

product_product()

class product_packaging(osv.osv):

    _inherit = 'product.packaging'

    def _check_ean_key(self, cr, uid, ids, context=None):
        return True

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean'])]

product_packaging()
