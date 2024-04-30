{
    'name': "FACTURACION DIRNEA",
    'summary': "Ecuadorian electronic invoice",
    'description': """
    TODO: add description
    """,
    'author': "Duodata",
    'website': "https://duodata.io/",
    'category': 'l10n_ec',
    'version': '16.0.1.0.0',
    'depends': [
        'tramite',
        'usuarios',
        'l10n_ec_sri_factura',
        'recaudacion'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/caja_views.xml',
        'views/sale_order_views.xml',
        'views/account_payment_views.xml',
        'wizard/apertura_cierre_caja_wizard.xml',
        'wizard/report.xml',
        'wizard/anular_pagos_wizard_views.xml',
    ]
}
