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


{
    'name': 'Requerimientos Fiscales AKR',
    'category': 'Account', 
    'version': '1.0',
    'description': """ 
Requerimientos Fiscales para Venezuela
====================================================
* Se modifica el formato de facturas de compra y venta adaptándolo a los requerimientos de AKR
    """,
    'author': 'Alexander Rodriguez',
    'website': '',
    'depends': ['l10n_ve_fiscal_requirements','account_invoice_shipping_address'],
    'data': [
            'view/report_invoice.xml',
            'account_invoice_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
