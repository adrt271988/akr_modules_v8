# -*- encoding: utf-8 -*-
import time

from openerp.addons import decimal_precision as dp
from openerp import models, fields, api, exceptions, _
from openerp.osv import osv


class inherited_account_wh_iva(models.Model):

    _inherit = "account.wh.iva"

    @api.multi
    def wh_iva_confirmed(self):
        """
        """
        self.write({'state': 'confirmed'})
        return True

    @api.multi
    def wh_iva_done(self):
        """Funcion redefinida para que obvie validacion original y
           continue poniendo como "done" la retencion
        """
        self.action_number()
        self.action_date_ret()
        try:
            self.action_move_create()
        except Exception, e:
            if 'ya ha sido retenida' in str(e):
                self.write({'state':'done'})
            else:
                raise
        return True

    @api.multi
    def action_cancel(self):
        """ Call cancel_move and return True
        """
        self.cancel_move()
        self.clear_wh_lines()
        return True
