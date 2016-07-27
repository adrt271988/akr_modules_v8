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
    "name" : "Adaptaciones en Productos para AKR.",
    "version" : "1.0",
    "author" : "Luis Torres (ltorres134@gmail)",
    "website" : "",
    "category": 'Product',
    "description": """
        -. Agrega campos en la ficha del producto.
        -. Crea restriciones de no duplicidad en el EAN13 y Referencia interna.
        -. Agrega 5 decimales a las cifras de empaquetados, peso y volumen.
    """,
    "depends" : [
                "base",
                "product"
                ],
    'data': [
        #"data/product_data.xml",
        "view/product_view.xml",
        "view/product_package_view.xml"
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
