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

class AkrIslrWhDocLine(osv.osv):
    _inherit = "islr.wh.doc.line"

    def _get_supplier_invoice_number(self, cr, uid, ids, fieldname, args, context=None):
        res = {}
        for iwdl_brw in self.browse(cr, uid, ids, context):
            if iwdl_brw.invoice_id:
                res[iwdl_brw.id] = iwdl_brw.invoice_id.supplier_invoice_number
        return res
        
    def _amount_without_withholding(self, cr, uid, ids, fieldname, args, context=None):
        res = {}
        for iwdl_brw in self.browse(cr, uid, ids, context):
            res[iwdl_brw.id] = {
                'amount_without_withholding': 0.0,
            }
            #~ if iwdl_brw.invoice_id:
        return res
    
    _columns = {
            'amount_without_withholding': fields.function(
            _amount_without_withholding, method=True, digits=(16, 2), string='Monto Exento',
            multi='all', help="Monto exento de retención ISLR"),
            'supplier_invoice_number': fields.function(
            _get_supplier_invoice_number, type='char', store=True, string='Factura de Proveedor', help="Factura de Proveedor"),
    }
