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
    "name" : "Modificaciones en Pagos AKR 58",
    "version" : "1.0",
    "author" : "Luis Torres",
    "website" : "",
    "category": "Pagos",
    "summary": "Adaptaciones Account Voucher",
    "description": """
                    - .\n
                    - .\n
                    - .
                  """,
    "depends" : [
                "account_voucher"
                ],
    'data': [
        "view/account_voucher.xml",
        #"view/customer_invoice.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
