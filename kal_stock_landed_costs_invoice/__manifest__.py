# -*- coding: utf-8 -*-
# Copyright 2022 Alonso Nuñez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock landed cost invoice",
    "version": "15.0.1.0.0",
    "author": "Jimmy Araujo",
    "license": "AGPL-3",
    'category': 'Inventory/Inventory',
    "depends": ['stock_landed_costs', 'stock', 'purchase'],
    "data": [
        'views/stock_landed_cost.xml'
    ],
    "installable": True,
}
