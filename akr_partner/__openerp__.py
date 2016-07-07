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
{
    "name" : "Adaptaciones en la Ficha de Partners para AKR",
    "version" : "1.0",
    "author" : "Luis Torres (ltorres134@gmail)",
    "website" : "",
    "category": 'Partner',
    "description": """
                    -. Agrega resticcion de no duplicidad en el campo referencia.
                    -. Reasigna campos a cualquier grupo en la pestaña contabilidad.
                   """,
    "depends" : [
                "base",
                "sale",
                "l10n_ve_fiscal_requirements",
                ],
    'data': [
        "view/partner_view.xml"
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
