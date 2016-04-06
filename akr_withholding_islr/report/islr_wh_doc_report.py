##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import time
from datetime import date
from datetime import datetime
from openerp.report import report_sxw
from openerp.tools.translate import _
from openerp.osv import osv


class report_islr_wh_doc(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(report_islr_wh_doc, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
            'get_fiscalyear': self._get_fiscalperiod,
            'split_string': self._split_string,
            'get_address': self._get_address,
            'get_doc_type': self._get_doc_type
        })
        self.context = context

    def _get_fiscalperiod(self, period_id, flag):
        res = ""
        if period_id:
            date = datetime.strptime(period_id.date_start, '%Y-%m-%d')
            if flag == "y":
                res = date.year
            if flag == "m":
                res = date.month
        return res
    
    def _get_doc_type(self, invoice_id):
        doc_type = ""
        if invoice_id.type == "in_refund":
            doc_type = "N.C."
        if invoice_id.type == "in_invoice" and invoice_id.parent_id:
            doc_type = "N.D."
        if invoice_id.type == "in_invoice" and not invoice_id.parent_id:
            doc_type = "F"
        return doc_type

    def _split_string(self, string, from_position):
        return string and string[from_position:] or ""

    def _get_address(self, street="", street2="", city="", state="", country=""):
        address = ""
        if street:
            address += street+", "
        if street2:
            address += street2+", "
        if city:
            address += city+", "
        if state:
            address += state+", "
        if country:
            address += country
        return address and address+"." or ""


class reportIslrWhDoc(osv.AbstractModel):
    _name = 'report.akr_withholding_islr.islr_wh_doc_report'
    _inherit = 'report.abstract_report'
    _template = 'akr_withholding_islr.islr_wh_doc_report'
    _wrapped_report_class = report_islr_wh_doc

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
