{
    'name': "Territorial Organization for Ecuador",
    'summary': "Install Ecuadorian Territorial Organization",
    'description': """
    TODO: add description
    """,
    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'l10n_ec',
    'version': '16',
    'application': True,
    'depends': [
        'base',
        'contacts',
        'base_address_extended',
        'l10n_ec',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res.country.state.csv',
        'data/res.city.csv',
        'data/res.country.csv',
        'views/l10n_ec_parish_views.xml',
        'views/res_country_views.xml',
        'views/res_city_views.xml',
        'views/res_partner.xml',
        'views/res_company_views.xml',

    ]
}