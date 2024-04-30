{
    'name': "Tráfico Marítimo Documento",
    'summary': "Documentos Tráfico Marítimo",
    'description': "Tráfico Marítimo",

    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'dirnea',
    'version': '1.0',

    """OPL-1 (Odoo Proprietary License v1.0)"""
    'license': "OPL-1",

    'depends': [
        'tramite',
        'trafico_maritimo',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/tramite.documento.csv',
        'views/documento_views.xml',
        'views/documento_emitido_views.xml',
        'views/tramite_views.xml',
        #'views/trafico_maritimo_navegacion_views.xml',
        'views/trafico_maritimo_arribo_views.xml',
        'views/trafico_maritimo_zarpe_views.xml',
        'views/trafico_maritimo_dotacion_views.xml',
        'views/trafico_maritimo_internacional_costera_views.xml',
        'views/menu_servicios.xml',
        'reports/report_paperformat.xml',
        'reports/trafico_maritimo_base_report_templates.xml',
        'reports/trafico_maritimo_zarpe_report_templates.xml',
        'reports/trafico_maritimo_zarpe_internacional_report_templates.xml',
        'reports/trafico_maritimo_arribo_report_templates.xml',
        'wizard/wizard_control_combustible_nave_views.xml',
        'wizard/ruta_geocoordenada_nave_wizard_views.xml',
    ],
    'images': [
        'static/src/img/escudoEcuador.jpg',
        'static/src/img/qr.jpg',
    ],
}
