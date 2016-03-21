#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Luis Torres.
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
    "name" : "Adaptaciones en Stock para AKR 58",
    "version" : "1.0",
    "author" : "Luis Torres",
    "website" : "ltorres134@gmail.com",
    "category": "Stock",
    "summary": "Modifica Stock Picking y Stock Move",
    "description": """
                        - Reporte Packing List.
                        - Restriccion de permisos en las operaciones de "Cancelar y Revertir" Transferencias.
                        - Restriccion de permisos en el botón "Forzar Disponibilidad".
                        - Oculta el campo Partner de las vistas.
                        - Agrega el campo llamado "Fecha de recepción."
                        - Coloca los campos "Transportista y Guía."
                        - Oculta el botón "Desechar Productos"."
                   """,
    "depends" : [
                "base",
                "stock",
                "delivery"
                ],
    'data': [
        "stock_report.xml",
        "view/stock_picking.xml",
        "view/stock_move.xml"
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
