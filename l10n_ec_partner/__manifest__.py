{
    'name': "Partner for Ecuador",
    'summary': "Partner identifier config",
    'description': """
    TODO: add description
    """,
    'author': "Duodata",
    'website': "https://duodata.io/",
    'category': 'l10n_ec',
    'version': '14.0.1.0.0',
    'depends': [
        'mail',
        'account',
        'l10n_latam_base',
        'l10n_latam_invoice_document',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/l10n_latam_identification_type_data.xml',
        'views/res_partner_views.xml',
        'data/res.bank.account.type.csv',
    ]
}
