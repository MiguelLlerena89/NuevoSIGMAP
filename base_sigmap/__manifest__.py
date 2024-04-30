{
    'name': "SIGMAP base",
    'summary': "SIGMAP base",
    'description': """
    TODO: add description
    """,
    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'mar',
    'version': '1.0',
    'depends': [
        'base',
        'mail',
        'account',
        'web',
        'l10n_ec_ote',
        'l10n_latam_base',
        'l10n_ec_sri',
        'export_view_pdf',
        'web_domain_field',
        ],
    #'assets': {
    #    'web.assets_backend': [
    #        ('after', 'base_sigmap/src/css/theme.css'),
    #    ],
    #    'web.assets_common': [
    #        ('after', 'base_sigmap/static/src/css/theme.css'),
    #        ('after', 'base_sigmap/static/src/scss/ui.scss'),
    #    ],
    #    'web._assets_primary_variables': [
    #        ('after', 'base_sigmap/static/src/scss/primary_variables_custom.scss'),
    #    ],
    #},
    'data': [
        'data/res.partner.parentesco.csv',
        'data/sigmap_documento_tipo.xml',
        'data/sigmap_secuencia_tipo.xml',
        'data/sigmap.reparto.tipo.csv',
        'data/sigmap.tipo.astillero.csv',
        'data/sigmap.tipo.construccion.csv',
        'data/tipo.trafico.csv',
        'data/sigmap.jurisdiccion.csv',
        'data/tipo.rango.csv',
        'security/ir.model.access.csv',

        'views/res_config_settings.xml',
        'views/report_background_config_view.xml',
        'data/default_settings.xml',

        'views/agencia_naviera_view.xml',
        'views/propietario_view.xml',
        'views/armador_view.xml',

        'views/tipo_trafico_view.xml',
        'views/tipo_fletamento_view.xml',

        'views/puerto_view.xml',
        'views/tipo_astillero_view.xml',
        'views/tipo_construccion_view.xml',
        'views/sociedad_clasificadora_view.xml',

        'views/reparto_tipo_view.xml',
        'views/reparto_view.xml',

        'views/base_res_partner_view.xml',
        'views/parentesco_views.xml',
        'views/tipo_documento_view.xml',
        'views/tipo_secuencia_view.xml',
        'views/tipo_rango_views.xml',

        #'views/base_sigmap_menus.xml',
        'views/web_layout.xml',
        'views/webcliente_templates.xml',
    ],
    'images': [
        'static/src/img/escudoEcuador.jpg',
        'static/src/img/ImagenEscudoEcuadorDocSize.jpg',
    ],
}
