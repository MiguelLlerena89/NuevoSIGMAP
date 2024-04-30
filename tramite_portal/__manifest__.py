# -*- coding: utf-8 -*-
{
    'name': "Trámite en línea",
    'author': "DIRNEA",
    'website': "https://www.dirnea.org",
    'category': 'DIRNEA',
    'version': '0.1',

    'depends': [
        'base_sigmap',
        'usuarios',
        'tramite',
    ],

    'data': [
        'data/res.users.csv',
        'data/tramite.documento.csv',
        'views/tramite_documento.xml',
    ],
}
