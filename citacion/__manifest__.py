{
    'name': "Citations",
    'summary': "Citations and Contraventions",
    'description': """
    TODO: add description
    """,
    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'mar',
    'version': '1.0',
    'depends': [
        'l10n_ec_ote',
        'l10n_ec_sri_factura',
        'base_sigmap',
        'personal_maritimo',
        'nave'
        ],
    'data': [
        'data/contravencion_ley_data.xml',
        'data/product_data.xml',

        'security/res_groups.xml',
        'security/ir.model.access.csv',

        'views/contravencion_ley_view.xml',
        'views/sancionado_ayuda.xml',
        'views/citacion_view.xml',
        'views/multa_view.xml',

        'views/citacion_menus.xml',
    ],
}
