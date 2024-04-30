
import base64
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

CERTIFICADOS = [
    ('autorizacion_cambio_nombre', 'Autorización cambio de Nombre de Nave'),
    ('cambio_propietario', 'Cambio Propietario'),
    ('cambio_puerto_registro', 'Cambio de Puerto de Registro'),
    ('cancelacion_gravamen_hipoteca', 'Cancelación de Gravamen e Hipoteca'),
    ('cancelacion_matricula', 'Cancelación de Matrícula (Baja de Nave)'),
    ('cancelacion_registro_interdiccion', 'Cancelación de Registro de Interdicción'),
    ('registro_nave_otra_capitania', 'Registro de Nave en otra Capitanía'),
    ('registro_propiedad', 'Registro de Propiedad'),
    ('historia_dominio', 'Historia de Dominio'),
    ('registro_gravamen_hipoteca', 'Registro de Gravamen e Hipoteca'),
    ('registro_interdiccion', 'Registro de Interdicción'),
    ('registro_inscripcion', 'Registro de Inscripción de embarcación por primera vez'),
    ('cambio_caracteristicas_tecnica', 'Cambio de características técnicas'),
    ('pasavante_navegacion', 'Pasavante Navegación'),
    ('patente_navegacion', 'Patente Navegación'),
    ('arqueo_nave', 'Arqueo de Nave'),
    ('prevencion_contaminacion', 'Seguridad y Prevención de la Contaminación'),
    ('buque_carga', 'Seguridad de Buques de Carga'),
    ('buque_pasaje', 'Seguridad de Pasaje'),
    ('linea_carga', 'Lineas de Carga'),
    ('radioelectrica', 'Seguridad Radioeléctrica'),
    ('dotacion_minima_seguridad', 'Dotación Mínima de Seguridad'),
    ('exencion', 'Exención'),
    ('prevencion_hidrocarburos', 'Prevención a la Contaminación por Hidrocarburos'),
    ('prevencion_aguas_sucias', 'Prevención a la Contaminación por Aguas Sucias'),
    ('declaracion_cumplimiento', 'Declaración de Cumplimiento'),
    ('gestion_seguridad', 'Gestión de Seguridad'),
    ('documento_cumplimiento', 'Documento de Cumplimiento'),
    ('registro_sinoptico_continuo', 'Registro Sinóptico Continuo del Buque [Pasaje >35 pax]'),
    ('proteccion_buque', 'Internacional de Protección del Buque (PBIP) [Pasaje >35 pax]'),
    #('inspeccion_dique_astillero', 'Inspección de dique en astilleros/varaderos nacional'),
    #('permiso_trafico', 'Permiso Tráfico Nacional/Internacional')
    ('manual_gestion_seguridad', 'Aprobación de Manual de Gestión de Seguridad (MGS)'),
    ('plan_proteccion_buque_portuaria', 'Aprobación de Plan PBIP (Buque/Instalación Portuaria)'),
    ('inf_tec_fav', _('Informe Técnico Favorable - Importacion/Nacionalización de Naves')),
    ('contr_fleta', _('Contrato de Fletamento')),
    ('contr_fleta_casco', _('Contrato de Fletamento a Casco desnudo')),
    ('contr_fleta_explo', _('Contrato de Fletamento por Exploración')),
    ('contr_asoci', _('Contrato de Asociación')),
    ('contr_int_temp', _('Contrato por Internación Temporal')),
    ('inf_tec_fav_contr', _('Informe Técnico Favorable - Naves con contrato de fletamento, asociación o arrendamiento')),
    ('rector_puerto', _('Supervisión Rector del Puerto')),
]


class NaveDocumentoCertificado(models.Model):
    _name = 'nave.documento.certificado'
    _description = 'Documento de Nave'
    _inherit = "nave.documento.base"

    READONLY_STATES = { state: [('readonly', True)] for state in {'vigente', 'caducado', 'anulado'}}

    nave_name = fields.Char(related='nave_id.name', string=_('Name Ship'), readonly=True, store=True, index=True, copy=False, tracking=True)
    senial_llamada = fields.Char(related='nave_id.senial_llamada', string=_('Distinctive Number o letters'), readonly=True, store=True, index=True, copy=False, tracking=True)
    #reparto_id = fields.Many2one(related='nave_id.reparto_id', string=_('Port of Registry'), readonly=True, store=True, index=True, copy=False, tracking=True)
    trb = fields.Float(related='nave_id.trb', string=_('Gross Tonnage'), readonly=True, store=True, index=True, copy=False, tracking=True)
    peso_muerto = fields.Float(related='nave_id.peso_muerto', string=_('Peso Muerto (t)'), readonly=True, store=True, index=True, copy=False, tracking=True)
    eslora = fields.Float(related='nave_id.eslora', string=_('Eslora (mts)'), readonly=True, store=True, index=True, copy=False, tracking=True)
    nave_zona_id = fields.Many2one(related='nave_id.nave_zona_id', string=_('Zona Marítima'), readonly=True, store=True, index=True, copy=False, tracking=True)
    omi_number = fields.Char(related='nave_id.omi_number', string=_('Número OMI'), readonly=True, store=True, index=True, copy=False, tracking=True)
    nave_tipo_id = fields.Many2one(related='nave_id.nave_tipo_id', string=_('Tipo Buque'), readonly=True, store=True, index=True, copy=False, tracking=True)
    fecha_coloco_quilla = fields.Date(string='Fecha en la que se colocó la quilla')

    # servicio_id = fields.Many2one(related='documento_emitido_id.tramite_id.servicio_id', readonly=True, store=True, index=True, copy=False, tracking=True)
    es_texto_html = fields.Boolean(related='documento_emitido_id.tramite_id.servicio_id.es_texto_html', readonly=True, store=True, index=True, copy=False, tracking=True)
    titulo = fields.Char(string=_('Título'), index=True, copy=False, tracking=True,states=READONLY_STATES)
    descripcion = fields.Html(string=_('Descripción'), index=True, copy=False, tracking=True,states=READONLY_STATES)

    tipo_certificado = fields.Selection(
        selection=CERTIFICADOS,
        string='Tipo Certificado',
        store=True,
        index=True,
        copy=False,
        tracking=True)
    # tipo_certificado = fields.Selection([
    #     ('autorizacion_cambio_nombre', 'Autorización de Cambio de Nombre'),
    #     ('cambio_propietario', 'Cambio Propietario'),
    #     ('cambio_puerto_registro', 'Cambio de Puerto de Registro'),
    #     ('cancelacion_gravamen_hipoteca', 'Cancelación de Gravamen e Hipoteca'),
    #     ('cancelacion_matricula', 'Cancelación de Matrícula (Baja de Nave)'),
    #     ('cancelacion_registro_interdiccion', 'Cancelación de Registro de Interdicción'),
    #     ('registro_nave_otra_capitania', 'Registro de Nave en otra Capitanía'),
    #     ('registro_propiedad', 'Registro de Propiedad'),
    #     ('historia_dominio', 'Historia de Dominio'),
    #     ('registro_gravamen_hipoteca', 'Registro de Gravamen e Hipoteca'),
    #     ('registro_interdiccion', 'Registro de Interdicción'),
    #     ('registro_inscripcion', 'Registro de Inscripción de embarcación por primera vez'),
    #     ('cambio_caracteristicas_tecnica', 'Cambio de características técnicas'),
    #     ('pasavante_navegacion', 'Pasavante Navegación'),
    #     ('patente_navegacion', 'Patente Navegación'),
    #     ('arqueo_nave', 'Arqueo de Nave'),
    #     ('prevencion_contaminacion', 'Seguridad y Prevención de la Contaminación'),
    #     ('buque_carga', 'Seguridad de Buques de Carga'),
    #     ('buque_pasaje', 'Seguridad de Pasaje'),
    #     ('linea_carga', 'Lineas de Carga'),
    #     ('radioelectrica', 'Seguridad Radioeléctrica'),
    #     ('dotacion_minima_seguridad', 'Dotación Mínima de Seguridad'),
    #     ('exencion', 'Exención'),
    #     ('prevencion_hidrocarburos', 'Prevención a la Contaminación por Hidrocarburos'),
    #     ('prevencion_aguas_sucias', 'Prevención a la Contaminación por Aguas Sucias'),
    #     ('declaracion_cumplimiento', 'Declaración de Cumplimiento'),
    #     ('gestion_seguridad', 'Gestión de Seguridad'),
    #     ('documento_cumplimiento', 'Documento de Cumplimiento'),
    #     ('registro_sinoptico_continuo', 'Registro Sinóptico Continuo del Buque [Pasaje >35 pax]'),
    #     ('proteccion_buque', 'Internacional de Protección del Buque (PBIP) [Pasaje >35 pax]'),
    #     #('inspeccion_dique_astillero', 'Inspección de dique en astilleros/varaderos nacional'),
    #     #('permiso_trafico', 'Permiso Tráfico Nacional/Internacional'),
    # ], string='Tipo Certificado', index=True, copy=False, tracking=True)

    es_provisional = fields.Boolean('¿Es Provisional?', copy=False, index=True, tracking=True)

    def validar(self):
        msg = ''
        if self.es_texto_html:
            if not self.titulo:
                msg = msg + 'Debe definir texto del título del certificado jurídico.\n'
            if not self.descripcion:
                msg = msg + 'Debe definit texto de la descripción del certificado jurídico.\n'
        if msg:
            raise ValidationError(_(msg))
        return True

    def get_tipo_code_from_tramite_documento(self, servicio):
        tipo = code = ''
        if servicio.id == self.env.ref("tramite.tramite_documento_129").id:
            code = "documento_autorizacion_cambio_nombre_code"
            tipo = 'autorizacion_cambio_nombre'
        if servicio.id == self.env.ref("tramite.tramite_documento_133").id:
            code = "documento_cambio_propietario_code"
            tipo = 'cambio_propietario'
        if servicio.id == self.env.ref("tramite.tramite_documento_132").id:
            code = "documento_cambio_puerto_registro_code"
            tipo = 'cambio_puerto_registro'
        if servicio.id == self.env.ref("tramite.tramite_documento_134").id:
            code = "documento_cancelacion_gravamen_hipoteca_code"
            tipo = 'cancelacion_gravamen_hipoteca'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_nave_matri_baja").id:
            code = "documento_cancelacion_matricula_code"
            tipo = 'cancelacion_matricula'
        if servicio.id == self.env.ref("tramite.tramite_documento_137").id:
            code = "documento_cancelacion_registro_interdiccion_code"
            tipo = 'cancelacion_registro_interdiccion'
        if servicio.id == self.env.ref("tramite.tramite_documento_146").id:
            code = "documento_registro_nave_otra_capitania_code"
            tipo = 'registro_nave_otra_capitania'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_reg_prop").id:
            code = "documento_registro_propiedad_code"
            tipo = 'registro_propiedad'
        if servicio.id == self.env.ref("tramite.tramite_documento_145").id:
            code = "documento_historia_dominio_code"
            tipo = 'historia_dominio'
        if servicio.id == self.env.ref("tramite.tramite_documento_181").id:
            code = "documento_registro_gravamen_hipoteca_code"
            tipo = 'registro_gravamen_hipoteca'
        if servicio.id == self.env.ref("tramite.tramite_documento_183").id:
            code = "documento_registro_interdiccion_code"
            tipo = 'registro_interdiccion'
        if servicio.id == self.env.ref("tramite.tramite_documento_182").id:
            code = "documento_registro_inscripcion_code"
            tipo = 'registro_inscripcion'
        # if servicio.id == self.env.ref("tramite.tramite_documento_230").id:
        #     code = "documento_cambio_caracteristicas_tecnica_code"
        #     tipo = 'cambio_caracteristicas_tecnica'
        if servicio.id == self.env.ref("tramite.tramite_documento_177").id:
            code = "documento_pasavante_navegacion_code"
            tipo = 'pasavante_navegacion'
        if servicio.id == self.env.ref("tramite.tramite_documento_178").id:
            code = "documento_patente_navegacion_code"
            tipo = 'patente_navegacion'
        if servicio.id in [self.env.ref("tramite.tramite_documento_139").id, self.env.ref("tramite.tramite_documento_140").id,self.env.ref("tramite.tramite_documento_141").id]:
            code = "documento_arqueo_code"
            tipo = 'arqueo_nave'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_nave_segu_prev").id:
            code = "documento_seguridad_prevencion_contaminacion_code"
            tipo = 'prevencion_contaminacion'
        if servicio.id == self.env.ref("tramite.tramite_documento_156").id:
            code = "documento_seguridad_buques_carga_code"
            tipo = 'buque_carga'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_nave_segu_pasaje").id:
            code = "documento_seguridad_buque_pasaje_code"
            tipo = 'buque_pasaje'
        if servicio.id == self.env.ref("tramite.tramite_documento_170").id:
            code = "documento_lineas_carga_code"
            tipo = 'linea_carga'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_nave_segu_radio").id:
            code = "documento_seguridad_radioelectrica_buque_code"
            tipo = 'radioelectrica'
        if servicio.id == self.env.ref("tramite.tramite_documento_143").id:
            code = "documento_dotacion_minima_seguridad_code"
            tipo = 'dotacion_minima_seguridad'
        if servicio.id == self.env.ref("tramite.tramite_documento_144").id:
            code = "documento_exencion_code"
            tipo = 'exencion'
        if servicio.id == self.env.ref("tramite.tramite_documento_164").id:
            code = "documento_prevencion_hidrocarburos_code"
            tipo = 'prevencion_hidrocarburos'
        if servicio.id == self.env.ref("tramite.tramite_documento_167").id:
            code = "documento_prevencion_contaminacion_aguas_sucias_code"
            tipo = 'prevencion_aguas_sucias'
        if servicio.id == self.env.ref("tramite.tramite_documento_142").id:
            code = "documento_declaracion_cumplimiento_code"  if not es_provisional else "documento_declaracion_cumplimiento_provisional_code"
            tipo = 'declaracion_cumplimiento'
        if servicio.id == self.env.ref("tramite.tramite_documento_126").id:
            code = "documento_gestion_seguridad_code" if not es_provisional else "documento_gestion_seguridad_provisional_code"
            tipo = 'gestion_seguridad'
        if servicio.id == self.env.ref("tramite.tramite_documento_127").id:
            code = "documento_documento_cumplimiento_code" if not es_provisional else "documento_documento_cumplimiento_provisional_code"
            tipo = 'documento_cumplimiento'
        if servicio.id == self.env.ref("tramite.tramite_documento_186").id:
            code = "documento_registro_sinoptico_continuo_code"
            tipo = 'registro_sinoptico_continuo'
        if servicio.id == self.env.ref("tramite.tramite_documento_187").id:
            code = "documento_internacional_proteccion_buque_code"
            tipo = 'proteccion_buque'
        if servicio.id in [self.env.ref("tramite.tramite_documento_179").id, self.env.ref("tramite.tramite_documento_180").id]:
            code = "documento_permiso_trafico_code"
            tipo = 'permiso_trafico'
        if servicio.id == self.env.ref("tramite.tramite_documento_112").id:
            code = "documento_manual_gestion_seguridad_code"
            tipo = 'manual_gestion_seguridad'
        if servicio.id == self.env.ref("tramite.tramite_documento_117").id:
            code = "documento_plan_proteccion_buque_portuaria_code"
            tipo = 'plan_proteccion_buque_portuaria'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_inf_tec_fav").id:
            code = 'documento_inf_tec_fav_code'
            tipo = 'inf_tec_fav'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_fleta").id:
            code = 'documento_contrato_fletamento_code'
            tipo = 'contr_fleta'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_fleta_casco").id:
            code = 'documento_contr_fleta_casco_code'
            tipo = 'contr_fleta_casco'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_fleta_explo").id:
            code = 'documento_contr_fleta_explo_code'
            tipo = 'contr_fleta_explo'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_asoci").id:
            code = 'documento_contrato_asociacion_code'
            tipo = 'contr_asoci'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_int_temp").id:
            code = 'documento_contr_int_temp_code'
            tipo = 'contr_int_temp'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_inf_tec_fav_contr").id:
            code = 'documento_inf_tec_fav_contr_code'
            tipo = 'inf_tec_fav_contr'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_nave_rector_puerto").id:
            code = 'documento_rector_puerto_code'
            tipo = 'rector_puerto'

        return tipo, code

    @api.model
    def create(self, vals):
        documento_emitido_id = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
        servicio = documento_emitido_id.tramite_id.servicio_id

        tipo, code = self.get_tipo_code_from_tramite_documento(servicio)
        if len(code) == 0:
            raise ValidationError(_('No existe secuencial para ese servicio.'))

        vals['es_provisional'] = vals.get('es_provisional', False) or servicio.es_provisional
        vals["tipo_certificado"] = tipo
        vals["name"] = self._get_seq_with_company(code)

        return super().create(vals)

    @api.model
    def validar_como_requerido(self, **kwargs):
        # Busca documento emitido vigente (nave)
        model = kwargs['model']
        nave_id = kwargs['nave_id']
        servicio_id = kwargs['servicio_id']

        tipo, code = self.get_tipo_code_from_tramite_documento(servicio_id)

        dom = [
            ('state', '!=', 'utilizado'),
            ('nave_id', '=', nave_id.id),
            ('tipo_certificado', '=', tipo),
        ]

        record = self.env[model].search(dom, limit=1, order='create_date desc')
        es_completado = record and (record.state == 'vigente')
        return record, es_completado

    _sql_constraints = [
        ('documento_certificado_uniq', 'unique (documento_emitido_id)', ('El certificado para la nave debe ser único.'))
    ]

    def action_recargar_descripcion(self):
        if self.es_texto_html and self.documento_emitido_id.tramite_id.servicio_id.plantilla_texto:
            self.descripcion = self.nave_id.llenar_plantilla(self.documento_emitido_id.tramite_id.servicio_id.plantilla_texto)
        else:
            raise UserError(
                _("El tipo de documento no es el correcto para realizar esta acción. Revise que:\n" + \
                  "  - La casilla 'Adicionar Título y Texto HMTL' esté marcada.\n" + \
                  "  - El campo 'Plantilla' esté configurado de la manera correcta."
                ))
