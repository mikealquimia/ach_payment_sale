# -*- coding: utf-8 -*-
{
    'name': "Sales Advances",
    'summary': """ This module helps to add sales advances without the need to create an invoice""",
    'description': """
        With this module we can:
            - Add payments from a confirmed sale.
            - View sales order advances.
            - Add advances with a different customer for sale.
            - Add the advances to the invoice(s) of the sale regardless of whether they are not from the same contact as the invoice.
            - Limit the amount of advances based on the total sale.
        """,
    'author': "Gt Alchemy Development",
    'license': 'LGPL-3',
    'category': 'Sales',
    'version': '0.1',
    'price': 10.00,
    'currency': 'USD',
    'depends': ['base',
                'account',
                'sale',
                'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/payment_sale.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/account_payment_views.xml',
        'views/account_invoice_views.xml',
        'data/ir_cron.xml',
    ],
}