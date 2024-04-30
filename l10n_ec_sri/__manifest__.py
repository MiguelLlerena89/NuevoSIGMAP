{
    'name': "Ecuadorian SRI",
    'summary': "SRI",
    'description': """
    TODO: add description
    """,
    'author': "Duodata",
    'website': "https://duodata.io/",
    'category': 'l10n_ec',
    'version': '16.0.1.0.0',
    'depends': [
        'mail',
        'account',
        'web',
        'l10n_ec',
        'l10n_ec_partner',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/sri_autorizacion.xml',
        'views/sri_comprobante_views.xml',
        'views/menu_sri_autorizacion.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
        'data/res.country.csv',
        'data/mail_templates_data.xml',
        'data/account_tax_group_data.xml',
        'data/account_tax_template_data.xml',
        'views/account_tax_views.xml',
        'data/default_settings.xml',
        'data/sri.payment.type.csv',
    ],
}
