{
    'name': "Recaudacion",
    'summary': "Recaudaciones de Tramites en Linea",
    'description': "Recaudaciones de Tramites en Linea",

    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'dirnea',
    'version': '1.1',

    """OPL-1 (Odoo Proprietary License v1.0)"""
    'license': "OPL-1",

    'depends': ['base','tramite', 'l10n_ec_sri'],

    'data': [
        'data/account_payment_method.xml',
        'data/mail_templates_sale_order_tramite.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/recaudacion_view.xml',
        'views/recaudacion_account_payment_view.xml',
        'views/recaudacion_manual_wizard_view.xml',
        'views/account_journal_views.xml'
    ],
}
