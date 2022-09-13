# -*- coding: utf-8 -*-
# Copyright 2022 Alonso Nuñez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kal Ticket Payment",
    "version": "15.0.1.0.0",
    "author": "Jimmy Araujo",
    "license": "AGPL-3",
    # "website": "https://github.com/OCA/web",
    "depends": ['account'],
    "data": [
        'report/rpt_custom_ticket_payment.xml',
    ],
    'assets': {
        'web.assets_backend': [

        ]
    },
    "installable": True,
}