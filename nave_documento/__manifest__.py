{
    'name': "Documentos de Naves",
    'summary': "Certificados y Documentos de las naves",
    'description': """
    TODO: add description
    """,
    'author': "DIRNEA",
    'website': "https://www.dirnea.org/",
    'category': 'mar',
    'version': '1.0',
    'depends': [
        'personal_maritimo_documento',
        'tramite',
        'nave',
        'usuarios'
        ],
    'data': [
        'data/sequence.xml',
        'data/nave.empresa.mantenimiento.clasificacion.csv',
        'data/nave.empresa.mantenimiento.tipo.csv',
        'data/nave.empresa.mantenimiento.uso.csv',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/tramite.documento.csv',
        'data/tramite.documento.requisito.csv',
        'data/product.template.csv',
        'data/rubro.tarifa.csv',
        'data/rubro.regla.csv',
        'views/documento_emitido_views.xml',
        'views/nave_lista_autorizada_views.xml',
        'views/nave_dotacion_minima_views.xml',
        'views/nave_nave_views.xml',
        'views/nave_convenio.xml',
        'views/nave_deficiencia.xml',
        'views/nave_lista_chequeo_views.xml',
        'views/tramite_documento_views.xml',
        'views/nave_inspeccion_views.xml',
        'views/tramite_views.xml',
        'views/nave_matricula_views.xml',
        'views/nave_documento_certificado_views.xml',
        'views/nave_documento_oficio_views.xml',
        'views/nave_vare_desvare_views.xml',
        'views/nave_empresa_mantenimiento.xml',
        'views/nave_domain_regla.xml',
        'views/menus.xml',
        'views/menu_servicios.xml',
        'wizard/genera_secuencia_nave_wizard_views.xml',
        'wizard/lista_chequeo_crea_pregunta_views.xml',
        'wizard/inspeccion_start_views.xml',
        'reports/report_paperformat.xml',
        #'reports/custom_ship_report_footer_templates.xml',
        'reports/nave_documento_base_report_templates.xml',
        'reports/nave_documento_base_oficio_templates.xml',
        'reports/nave_matricula_report_templates.xml',
        'reports/nave_certificado_arqueo_report_templates.xml',
        'reports/nave_seguridad_prevencion_contaminacion_templates.xml',
        'reports/nave_seguridad_buque_carga_templates.xml',
        'reports/nave_seguridad_buque_pasaje_templates.xml',
        'reports/nave_seguridad_radioeletrica_templates.xml',
        'reports/nave_dotacion_minima_seguridad_templates.xml',
        'reports/nave_exencion_templates.xml',
        'reports/nave_prevencion_contaminacion_hidrocarburos_templates.xml',
        'reports/nave_prevencion_contaminacion_aguas_sucias_report_templates.xml',
        'reports/nave_declaracion_cumplimiento_templates.xml',
        'reports/nave_gestion_seguridad_templates.xml',
        'reports/nave_documento_cumplimiento_templates.xml',
        'reports/nave_registro_sinoptico_continuo_templates.xml',
        'reports/nave_proteccion_buque_templates.xml',
        'reports/nave_lineas_carga_templates.xml',
        'reports/nave_vare_desvare_templates.xml',
        'reports/nave_registro_propiedad_templates.xml',
        'reports/nave_pasavante_navegacion_templates.xml',
        'reports/nave_patente_navegacion_templates.xml',
        'reports/nave_cuadro_zafarrancho_templates.xml',
        'reports/nave_aprobacion_manual_gestion_seguridad_templates.xml',
        'reports/nave_aprobacion_plan_proteccion_buque_portuaria_templates.xml',
        'reports/nave_lista_chequeo_templates.xml',
    ],
    'css': [
        'static/src/css/styles.css',
    ],
}