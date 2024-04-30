{
    'name': "Ecuadorian electronic invoice",
    'summary': "Ecuadorian electronic invoice",
    'description': """
    TODO: add description
    """,
    'author': "Duodata",
    'website': "https://duodata.io/",
    'category': 'l10n_ec',
    'version': '16.0.1.0.0',
    'depends': [
        'l10n_ec_sri',
        'web_domain_field',
        'eq_allow_cancel_journal_entries',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/sri_comprobante_views.xml',
    ]
}
