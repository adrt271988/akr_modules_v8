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

    def create(self, cr, uid, values, context=None):
        print 'Por create >>>>>>>>>>>>>>>>>>>>>>>'

        if (values.get('partner_type') == 'NR' or values.get('partner_type') == 'NN') and values.get('vat')[2].upper() != 'V':
            raise osv.except_osv(_('Error!'), 'El RIF de Persona Natural debe comenzar con las siglas "VEV"')
        if (values.get('partner_type') == 'JD' or values.get('partner_type') == 'JN') and values.get('vat')[2].upper() != 'J':
            raise osv.except_osv(_('Error!'), 'El RIF de Persona Jurídica debe comenzar con las siglas "VEJ"')
        if not values.get('validated',False):
            values['validated'] = True
        return super(inherit_res_partner, self).create(cr, uid, values, context=context)

    #~ def write(self, cr, uid, ids, vals, context=None):
        #~ print '============',vals
        #~ if (vals.get('partner_type') == 'NR' or vals == 'NN') and vals.get('vat')[3].upper() != 'V':
            #~ raise osv.except_osv(_('Error!'), 'El RIF de Persona Natural debe comenzar con las siglas "VEV"')
        #~ elif (vals.get('partner_type') == 'JD' or vals == 'JN') and vals.get('vat')[3].upper() != 'J':
            #~ raise osv.except_osv(_('Error!'), 'El RIF de Persona Jurídica debe comenzar con las siglas "VEJ"')
#~
        #~ return super(inherit_res_partner, self).write(cr, uid, ids, vals, context=context)

    _columns = {
                'validated': fields.boolean('Validado'),
                'partner_type': fields.selection([ ('NR', 'Natural - Residente'),
                                                    ('NN', 'Natural - No residente'),
                                                    ('JD', 'Jurídica - Domiciliada'),
                                                    ('JN', 'Jurídica - No domiciliada')], 'Tipo'),

                }

    def vat_change(self, cr, uid, ids, value, context=None):
        print 'Por vat_change >>>>>>>>>>>>>>>>>>>>>>>'
        if value and value[:2].upper() != 'VE':
            raise osv.except_osv(_('warning!'), 'Todo RIF a ingresar debe comenzar con las siglas "VE"')
        return {'value': {'vat_subjected': bool(value)}}

    def type_change(self, cr, uid, ids, value, context=None):
        partner = self.browse(cr, uid, ids, context)
        if value:
            if not partner.vat:
                raise osv.except_osv(_('warning!'), 'Recuerde Validar RIF antes de guardar!')
            else:
                if (value == 'NR' or value == 'NN') and partner.vat[2].upper() != 'V':
                    raise osv.except_osv(_('warning!'), 'Todo RIF de Persona Natural debe comenzar con las siglas "VEV"')
                elif (value == 'JD' or value == 'JN') and partner.vat[2].upper() != 'J':
                    raise osv.except_osv(_('warning!'), 'Todo RIF de Persona Jurídica debe comenzar con las siglas "VEJ"')
                else:
                    return True
        return True


    _sql_constraints = [
        ('default_vat_uniq', 'unique(vat)', 'El RIF que desea almacenar ya está asignado a un partner!'),
        ('default_reference_uniq', 'unique(ref)', 'Reference must be unique per partner!'),
    ]

inherit_res_partner()
