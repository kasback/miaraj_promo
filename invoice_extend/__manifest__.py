# -*- coding: utf-8 -*-

{
    "name": "Invoice extend",
    "version": "1.1",
    "depends": ['base', 'purchase', 'account', 'product', 'stock', 'snailmail_account'],
    "author": "Nacer",
    'website': '',
    "category": "",
    "description": "",
    "init_xml": [],
    'data': [
        'views/account_invoice_view.xml',
        'views/report_invoice.xml',
        'views/product_template_views.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
