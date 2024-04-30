{
    'name': "Departamentos DIRNEA",
    'summary': "Estructura DIRNEA",
    'description': """
    TODO: add description
    """,
    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'dirnea',
    'version': '1.0',
    'depends': [
        'base_setup',
        'mail',
        'web',
        'base_sigmap',
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/departamento_dirnea_views.xml',
        'views/menuitem.xml',
    ],
}
