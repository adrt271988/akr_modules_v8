#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Luis Torres (ltorres134@gmail.com).
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


class inherit_res_partner(osv.osv):

    _inherit = 'res.partner'

    def write(self, cr, uid, ids,values, context=None):
        if values.get('partner_type') == 'NR' and values.get('vat')[2].upper() not in ['V','E']:
            raise osv.except_osv(_('Error!'), 'El RIF de Persona Natural debe comenzar con las siglas "VEV"')
        if values.get('partner_type') == 'JD' and values.get('vat')[2].upper() not in ['J','G']:
            raise osv.except_osv(_('Error!'), 'El RIF de Persona Jurídica debe comenzar con las siglas "VEJ"')
        if not values.get('validated',False):
            values['validated'] = True
        return super(inherit_res_partner, self).write(cr, uid, ids, values, context=context)

    _columns = {
                'validated': fields.boolean('Validado'),
                'partner_type': fields.selection([ ('NR', 'Natural - Residente'),
                                                    ('NN', 'Natural - No residente'),
                                                    ('JD', 'Jurídica - Domiciliada'),
                                                    ('JN', 'Jurídica - No domiciliada')], 'Tipo'),

                }

    _defaults = {
                'partner_type': 'NR',
    }

    def button_check_vat(self, cr, uid, ids, context=None):
        partner = self.browse(cr, uid, ids, context)
        if partner.partner_type == 'NR' and partner.vat[2].upper() not in ['V','E']:
            raise osv.except_osv(_('warning!'), 'Todo RIF de Persona Natural debe comenzar con las siglas "VEV"')
        elif partner.partner_type == 'JD' and partner.vat[2].upper() not in ['J','G']:
            raise osv.except_osv(_('warning!'), 'Todo RIF de Persona Jurídica debe comenzar con las siglas "VEJ o VEG"')
        else:
            self.write(cr, uid, ids, {'validated':True}, context = context)
        return super(inherit_res_partner, self).button_check_vat(cr, uid, ids, context=context)


    _sql_constraints = [
        ('default_vat_uniq', 'unique(vat)', 'El RIF que desea almacenar ya está asignado a un partner!'),
        ('default_reference_uniq', 'unique(ref)', 'Reference must be unique per partner!'),
    ]

inherit_res_partner()
