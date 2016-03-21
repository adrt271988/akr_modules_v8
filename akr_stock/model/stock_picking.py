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

from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.addons.procurement import procurement
import logging


class inherit_stock_picking(osv.osv):
    
    _inherit ="stock.picking"
    _description = "Herencia Stock Picking"
    _columns = {
                    'date_reception': fields.datetime('Fecha de recepción', help="Fecha en la cual se recibio la mercancia.",readonly=True, states={'done': [('readonly', False)]}, copy=False),
                    'origin': fields.char('Source Document',readonly=True, states={'draft': [('readonly', False)]}, help="Reference of the document", select=True),
                    'location_dest_id': fields.related('move_lines', 'location_dest_id', type='many2one', relation='stock.location', string='Destination Location', readonly=True),
                 }
inherit_stock_picking()
