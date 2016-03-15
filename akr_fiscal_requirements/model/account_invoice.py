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

import itertools
from lxml import etree
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
#~ from openerp.osv import fields, osv

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')

class akrFiscalAccountInvoice(models.Model):
    _inherit = "account.invoice"
    #~ @api.multi
    #~ def get_journal_type(self, cr, uid, ids, name, arg, context=None):
        #~ print 'entre!!!!!!!!!!!!'
        #~ if self:
            #~ for invoice in self:
                #~ context = invoice._context
                #~ if context.get('journal_type'):
                    #~ print '*************',context['journal_type']
                    #~ invoice.journal_type = context['journal_type']
                #~ else:
                    #~ print '************',invoice.journal_id
                    #~ invoice.journal_type = invoice.journal_id and invoice.journal_id.type or False
    
    journal_type = fields.Char(string='Tipo de Diario',default=lambda self: self._context.get('journal_type'))
