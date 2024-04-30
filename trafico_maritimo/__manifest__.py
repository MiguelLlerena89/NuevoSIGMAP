{
    'name': "Trafico Maritimo",
    'summary': "Trafico Maritimo",
    'description': "Trafico Maritimo",

    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'dirnea',
    'version': '1.0',

    """OPL-1 (Odoo Proprietary License v1.0)"""
    'license': "OPL-1",

    'depends': [
        'base',
        'mail',
        'web',
        'sale_management',
        'account',
        'l10n_ec',
        'l10n_ec_ote',
        'l10n_latam_base',
        'base_sigmap',
        'personal_maritimo',
        'nave',
        'usuarios'
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/iaa/instruction_views.xml',
        'views/iaa/vessel_voyage_information_views.xml',
        'views/iaa/general_declaration_views.xml',
        'views/iaa/cargo_declaration_fal_2_views.xml',
        'views/iaa/ship_store_declaration_fal_3_views.xml',
        'views/iaa/crew_effects_declaration_fal_4_views.xml',
        'views/iaa/crew_list_declaration_fal_5_views.xml',
        'views/iaa/passenger_list_declaration_fal_6_views.xml',
        'views/iaa/dangerous_load_fal_7_views.xml',
        'views/iaa/measures_procedures_views.xml',
        'views/iaa/maritime_declaration_heath_views.xml',
        'views/iaa/crew_vaccunated_list_views.xml',
        'views/iaa/nill_list_views.xml',
        'views/nave_nave_construccion_views.xml',
        'views/nave_nave_views.xml',
        'views/trafico_maritimo_ruta_views.xml',
        'views/trafico_maritimo_navegacion_views.xml',
        'views/trafico_maritimo_internacional_costera_views.xml',
        'views/menuitem.xml',
        'wizard/registrar_posicion_coordenada_wizard_views.xml',
    ],
}