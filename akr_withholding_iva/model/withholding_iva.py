# -*- encoding: utf-8 -*-
from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp
import time


class inherited_account_wh_iva(osv.osv):
    
    _inherit = "account.wh.iva"
    _columns = {
               }

inherited_account_wh_iva()



