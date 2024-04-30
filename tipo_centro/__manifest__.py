{
    'name': "Centros",
    'summary': "Centros",
    'description': """
    TODO: add description
    """,
    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'personalmar',
    'version': '1.0',
    'depends': [
        'mail',
        'web',
        'l10n_ec_ote',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/centro_medico_views.xml',
        'views/centro_formacion_views.xml',
        'data/centro.formacion.csv',
        'data/centro.medico.csv',
    ],
}
