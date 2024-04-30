{
    'name': "Naves",
    'summary': "Gestion de Naves, servicios y certificados",
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
        'sale_management',
        'account',
        'l10n_ec_ote',
        'tipo_centro',
        'l10n_ec',
        'l10n_latam_base',
        'base_sigmap',
        ],
    'data': [
        'data/nave.canal.banda.csv',
        'data/nave.casco.material.csv',
        'data/nave.dispositivo.modelo.tipo.clase.csv',
        'data/nave.nave.clase.matricula.csv',
        'data/nave.nave.foto.tipo.csv',
        'data/nave.nave.grupo.csv',
        'data/nave.nave.origen.csv',
        'data/nave.nave.servicio.csv',
        'data/nave.nave.tipo.csv',
        'data/nave.nave.zona.csv',
        'data/nave.nave.estado.csv',
        'data/nave.tipo.propulsion.csv',
        'data/default_settings.xml',

        'security/ir.model.access.csv',
        'security/res.groups.xml',

        'views/nave_casco_material.xml',
        'views/nave_clase_matricula_view.xml',
        'views/nave_grupo_views.xml',
        'views/nave_origen_view.xml',
        'views/nave_servicio_view.xml',
        'views/nave_tipo_propulsion_view.xml',
        'views/nave_tipo_view.xml',
        'views/nave_zona.xml',

        'views/nave_canal_frecuencia.xml',

        'views/nave_view.xml',
        'views/nave_constructor_view.xml',
        'views/nave_dispositivo_view.xml',

        'views/nave_motor_view.xml',

        'views/nave_foto_view.xml',
        'views/nave_matricula_bitacora_views.xml',

        'views/res_config_settings.xml',

        'views/nave_menus.xml',

        'views/sigmap_agencia.xml',
        'views/sigmap_propietario_view.xml',
        'views/sigmap_armador_view.xml',
    ],
}
