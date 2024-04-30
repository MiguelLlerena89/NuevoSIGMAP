{
    'name': "Control suminitros",
    'summary': "Información de control de suministros",
    'description': """
    TODO: add description
    """,
    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'mar',
    'version': '1.0',
    'depends': [
        'mail',
        'web',
        'tramite',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/uom.suministro.csv',
        'views/control_suministro_views.xml',
        'views/menuitem.xml',
    ],
}
