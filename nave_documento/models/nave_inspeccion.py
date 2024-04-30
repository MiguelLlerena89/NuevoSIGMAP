from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
import json


class CalificacionAnulada(models.AbstractModel):
    _name = 'nave.inspeccion.calificacion.anulada'

    anulado_por = fields.Char("Anulada por", default="")

    anulado = fields.Char(compute='_compute_anulado', string='anulada')

    def _add_anulado_por(self, pregunta):
        self.ensure_one()
        current_lista = self.anulado_por.split(',') if self.anulado_por else []
        current_lista.append(str(pregunta))
        self.anulado_por = ','.join(current_lista)

    def _del_anulado_por(self, pregunta):
        self.ensure_one()
        current_lista = self.anulado_por.split(',') if self.anulado_por else []
        lista_limpia = list(set(current_lista) - set([str(pregunta)]))
        self.anulado_por = ','.join(lista_limpia) if len(lista_limpia) > 0 else ""

    def add_del_anulado_por(self, add, pregunta):
        self.ensure_one()
        if add:
            self._add_anulado_por(pregunta)
        else:
            self._del_anulado_por(pregunta)

    def clean_anulado_por(self):
        for rec in self:
            rec.anulado_por = ""

    @api.depends('anulado_por')
    def _compute_anulado(self):
        for rec in self:
            rec.anulado = rec.anulado_por != "" and len(rec.anulado_por.split(",")) > 0


class NaveInspeccion(models.Model):
    _name = 'nave.inspeccion'
    _description = _('Inspecciones de naves')
    _inherit = ['mail.thread', 'mail.activity.mixin', 'nave.inspeccion.calificacion.anulada']

    """
    "ID_INSPECCION_NAVE",

    "ID_USUARIO_INGRESO",
    "FECHA_INGRESO",
    "ID_USUARIO_MODIFICACION",
    "FECHA_MODIFICACION",

    "ID_TIPO_MODULO"
    "ID_FACTURA_FPROGRAMA",

    "ID_FACTURA",
    "ID_TRAMITE",

    "TIPO_INSPECCION",              RENO, ENDO

    "ID_REPARTO",
    "ID_PUERTO",
    "ID_NAVE",
    "ID_CERTIFICADO",
    "ID_LISTA_CHEQUEO",

    "FECHA_SOLICITUD_INSPECCION",
    "LUGAR_EMBARQUE",
    "LUGAR_INSPECCION",
    "FECHA_INSPECCION",

    "NOMBRES_CONTACTO",
    "DIRECCION_CONTACTO",
    "TELEFONO_CONTACTO",

    "ID_INSPECTOR",

    "CALIFICACION",

    "TIPO_SOLICITANTE",
    "ID_SOLICITANTE",
    "IDENTIFICACION_TRAMITADOR",
    "NOMBRES_TRAMITADOR",
    "REPRESENTANTE_LEGAL",

    "OBSERVACION",
    "OBJETIVO_RECONOCIMIENTO",
    "ESTADO",

    "ACOMPANAMIENTO",

    "ID_ARCHIVO"
    """

    # Nombre
    name = fields.Char(
        string=_('Name'),
        index=True,
        copy=False,
        tracking=True)


    tramite_id = fields.Many2one("tramite", "Tramite", tracking=True)


    reparto_id = fields.Many2one(related="tramite_id.reparto_id", string=_('Reparto'), readonly=True)
    servicio_id = fields.Many2one(related="tramite_id.servicio_id", string=_('Certificado'), readonly=True)
    tiene_condicional = fields.Boolean(related="tramite_id.servicio_id.tiene_condicional", string=_('¿Tiene Condicional?'), readonly=True)
    tipo_inspeccion = fields.Selection(related="tramite_id.tipo_inspeccion", string=_('Tipo Inspección'), readonly=True)

    nave_id = fields.Many2one(related="tramite_id.nave_id", string=_("Nave"), readonly=True)
    tipo_inspector_id = fields.Many2one(related='tramite_id.tipo_inspector_id', string=_('Tipo Inspector'))

    puerto_id = fields.Many2one("sigmap.puerto", "Puerto", tracking=True)

    lugar_inspeccion = fields.Char(
        string=_('Lugar de inspección'),
        tracking=True)
    lugar_embarque = fields.Char(
        string=_('Lugar de embarque'),
        tracking=True)
    contacto = fields.Char(
        string=_('Contacto'),
        tracking=True)
    telefono = fields.Char(
        string=_('Teléfono de contacto'),
        tracking=True)

    inspector_id = fields.Many2one("sigmap.inspector", "Inspector", tracking=True)
    lista_chequeo_id = fields.Many2one("lista.chequeo", "Lista chequeo", tracking=True)
    lista_chequeo_puntaje_max = fields.Integer(string=_("Puntaje Máximo"), related="lista_chequeo_id.puntaje_max")

    state = fields.Selection(
        [
            ('por_asignar_lista', _('Por asignar lista de chequeo')),
            ('por_asignar_inspector', _('Por asignar inspector')),
            ('por_coordinar', _('Por coordinar')),
            ('programada', _('Programada')),
            ('realizada', _('Realizada')),
            ('cancel', _('Cancelada')),
        ],
        default="por_asignar_lista",
        string=_('Estado'),
        tracking=True)

    fecha_inspeccion = fields.Datetime(
        string="Fecha inspeccion",
        tracking=True,
    )

    estado_lista_chequeo = fields.Selection(
        [
            ('por_asignar', _('Por asignar')),
            ('por_llenar', _('Por llenar')),
            ('llenando', _('Llenando')),
            ('solicitar_supervisor', _('Solicitar supervisor')),
            ('aprobado_satisfactorio', _('Aprobado Satisfactorio')),
            ('aprobado_condicional', _('Aprobado Condicional')),
            ('aprobado_no_satisfactorio', _('No Satisfactorio')),
        ],
        default="por_asignar",
        string=_('Estado lista chequeo'),
        tracking=True)

    lista_chequeo_pregunta_ids = fields.One2many("nave.inspeccion.pregunta", "inspeccion_id", string=("Lista de Chequeo"), tracking=True,
        domain=lambda self: self.get_domain_for_pregunta_ids)

    lista_para_llenar = fields.Boolean(_('lista para llenar?'), compute='compute_lista_por_llenar')

    lista_llenada = fields.Boolean(_('llena?'), compute='compute_lista_por_llenar')

    CALIFICACIONES = [
        ('sati', _('Satisfactoria')),
        ('cond', _('Satisfactoria Condicional')),
        ('nosa', _('No Satisfactoria')),
    ]

    puntaje_sistema = fields.Integer(
        string=_('Puntaje Calculado'),
        compute="compute_puntaje_calificacion",
        store=True)

    calificacion_sistema = fields.Selection(
        CALIFICACIONES,
        default="nosa",
        string=_('Calificación del Sistema'),
        compute="compute_puntaje_calificacion",
        store=True)

    calificacion_sugerida = fields.Selection(
        CALIFICACIONES,
        default=False,
        string=_('Calificación Sugerida'),
        tracking=True)

    calificacion_final = fields.Selection(
        CALIFICACIONES,
        default=False,
        string=_('Calificación Final'),
        tracking=True)

    pregunta_ids_domain = fields.Char(
        string=_('pregunta_ids domain'),
        compute='_compute_pregunta_ids_domain',
        store=True,
        precompute=True)


    @api.depends('state', 'lista_chequeo_pregunta_ids.respuesta')
    def get_domain_for_pregunta_ids(self):
        self.ensure_one()
        domain = [('id','=',-1)]
        if self.lista_chequeo_id or (self.state in ['por_asignar_inspector', 'por_coordinar', 'programada']):
            domain = [()]
        if self.state in ['programada','realizada']:
            domain = [('respuesta', 'in', ['obs', 'nos'])]
        return domain


    @api.depends('state')
    def _compute_pregunta_ids_domain(self):
        for rec in self:
            domain = rec.get_domain_for_pregunta_ids()
            rec.pregunta_ids_domain = json.dumps(domain)

    @api.depends('lista_chequeo_id', 'inspector_id', 'estado_lista_chequeo', 'state', 'lista_chequeo_pregunta_ids')
    def compute_lista_por_llenar(self):
        for rec in self:
            rec.lista_para_llenar = rec.lista_chequeo_id and rec.inspector_id and \
                rec.estado_lista_chequeo in ['por_llenar', 'llenando'] and rec.state == 'programada' and \
                rec.lista_chequeo_pregunta_ids

            llena = True
            for pregunta in rec.lista_chequeo_pregunta_ids:
                if not pregunta.get_respondida():
                    llena = False
                    break
            rec.lista_llenada = llena

    def _validate_lista_chequeo_id_change(self):
        self.ensure_one()
        if self.state not in ["por_asignar_lista", "por_asignar_inspector"]:
            raise ValidationError(_('Contacte a Soporte, ya no se puede modificar la lista de chequeo'))

    def _get_triplets_preguntas(self, lista_chequeo_id=None):
        self.ensure_one()
        triplets_preguntas = []

        lista = self.env['lista.chequeo'].browse(lista_chequeo_id) if lista_chequeo_id else self.lista_chequeo_id
        if lista:
            for grupo in lista.grupo_pregunta_ids:
                grupo_data = {
                    'display_type': 'line_section',
                    'name': f'{grupo.sequence}. {grupo.name}',
                    'resource_ref': f'{grupo._name},{grupo.id}',
                }
                triplets_preguntas.append((0, 0, grupo_data))
                for pregunta in grupo.pregunta_ids:
                    pregunta_name = pregunta.texto if pregunta.texto else pregunta.name
                    pregunta_data = {
                        'name': pregunta_name,
                        'resource_ref': f'{pregunta._name},{pregunta.id}',
                        'sequence_for_o2m_parent': pregunta.sequence_for_o2m_parent,
                        'sequence_for_o2m_child': pregunta.sequence_for_o2m_child,
                        'has_child_ids': pregunta.has_child_ids,
                    }
                    if not pregunta.has_child_ids:
                        pregunta_data['puntaje_no_satisfactorio'] = pregunta.get_puntaje_for_respuesta()

                    triplets_preguntas.append((0, 0, pregunta_data))

        return triplets_preguntas

    def _update_preguntas(self):
        self.write({"lista_chequeo_pregunta_ids": [(5,0,0)]})
        triplets_preguntas = self._get_triplets_preguntas()
        if triplets_preguntas:
            self.write({"lista_chequeo_pregunta_ids": triplets_preguntas})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("nave_inspeccion_sequence_code")
        records = super().create(vals_list)
        for rec in records:
            if rec.lista_chequeo_id:
                rec._update_preguntas()
        return records

    def _add_preguntas_to_vals(self, vals):
        if ('lista_chequeo_id' in vals) and vals['lista_chequeo_id']:
            triplets_preguntas = self._get_triplets_preguntas(vals['lista_chequeo_id'])
            if triplets_preguntas:
                vals["lista_chequeo_pregunta_ids"] = triplets_preguntas
        return vals

    def write(self, vals):
        if 'lista_chequeo_id' in vals:
            self._validate_lista_chequeo_id_change()
            self.write({"lista_chequeo_pregunta_ids": [(5,0,0)]})
            if vals['lista_chequeo_id']:
                vals = self._add_preguntas_to_vals(vals)
        return super().write(vals)

    @api.onchange('tramite_id')
    def _onchange_tramite_id(self):
        fields_list = ['puerto_id', 'lugar_inspeccion', 'lugar_embarque', 'contacto', 'telefono']
        if self.tramite_id:
            for field_name in fields_list:
                setattr(self, field_name, self.tramite_id[field_name])

    #@api.onchange('inspector_id')
    #def _onchange_inspector(self):
    #    self.state = 'por_coordinar' if self.inspector_id else 'por_asignar_inspector'

    @api.onchange('lista_chequeo_id')
    def _onchange_lista_chequeo(self):
        if self.lista_chequeo_id:
            self._validate_lista_chequeo_id_change()
            self.estado_lista_chequeo = "por_llenar"
            self._onchange_inspector()
        else:
            self.estado_lista_chequeo = "por_asignar"
            self.state = 'por_asignar_lista'

    def get_grupo_from_preguntas(self, grupo_id):
        if grupo_id and self.lista_chequeo_pregunta_ids:
            found_pregs = [preg for preg in self.lista_chequeo_pregunta_ids if preg.display_type == 'line_section' and preg.resource_ref.id == grupo_id]
            if found_pregs:
                return found_pregs[0]
        return False

    def get_pregunta_from_preguntas(self, pregunta_id):
        if pregunta_id and self.lista_chequeo_pregunta_ids:
            found_pregs = [preg for preg in self.lista_chequeo_pregunta_ids if not preg.display_type and preg.resource_ref.id == pregunta_id]
            if found_pregs:
                return found_pregs[0]
        return False

    def _calcular_puntos_menos_por_anulados(self):
        self.ensure_one()
        restar = 0
        padres_anulados = grupos_anulados = []
        for preg in self.lista_chequeo_pregunta_ids:
            if preg.anulado:
                if preg.display_type == 'line_section':
                    grupos_anulados.append(preg.resource_ref.id)
                    restar += preg.resource_ref.puntaje_max
                elif preg.has_child_ids and (preg.resource_ref.grupo_id.id not in grupos_anulados):
                    padres_anulados.append(preg.resource_ref.id)
                    restar += preg.puntaje_no_satisfactorio
            if not preg.display_type and not preg.has_child_ids:
                if preg.resource_ref.grupo_id.id in grupos_anulados \
                   or (preg.resource_ref.parent_id and preg.resource_ref.parent_id.id in padres_anulados) \
                   or preg.respuesta in ['sat', 'exe']:
                    continue
                else:
                    porcentaje = 1
                    if preg.deficiencia_id and not preg.deficiencia_id.anula_pregunta and preg.deficiencia_id.porcentaje_pregunta:
                        porcentaje = 1 - preg.deficiencia_id.porcentaje_pregunta
                    if not preg.deficiencia_id and preg.respuesta == 'obs':
                        porcentaje = 0.75

                    restar += preg.puntaje_no_satisfactorio * porcentaje
        return restar

    def get_calificacion_calculada(self):
        calificacion = self.puntaje_sistema
        calificacion_str = self.calificacion_sistema

        if not self.anulado and self.state in ['programada','realizada'] and self.estado_lista_chequeo not in ['por_asignar', 'por_llenar']:
            calificacion = self.lista_chequeo_id.puntaje_max
            calificacion_str = "sati"

            calificacion -= self._calcular_puntos_menos_por_anulados()

            if self.lista_chequeo_id.puntaje_min_satisfactorio > calificacion:
                if self.lista_chequeo_id.tiene_condicional and calificacion >= self.lista_chequeo_id.puntaje_min_condicional:
                    calificacion_str = "cond"
                else:
                    calificacion_str = "nosa"

        #if self.state == "realizada":
        #    calificacion = self.puntaje_sistema
        #    calificacion_str = self.calificacion_sistema

        return int(calificacion), calificacion_str

    @api.depends('state', 'estado_lista_chequeo', 'lista_chequeo_pregunta_ids')
    def compute_puntaje_calificacion(self):
        for rec in self:
            rec.puntaje_sistema = 0
            rec.calificacion_sistema = "nosa"
            if rec.state in ['programada','realizada'] and rec.estado_lista_chequeo not in ['por_asignar', 'por_llenar']:
                rec.puntaje_sistema, rec.calificacion_sistema = rec.get_calificacion_calculada()

    def action_coordinar(self):
        self.state = 'por_coordinar'

    def action_programar(self):
        self.state = 'programada'

    def generar_documento(self):
        doc_emitido = self.env[self.servicio_id.model_model].search([("tramite_id",'=',self.tramite_id.id)])
        if not doc_emitido:
            raise ValidationError(_('Comuníquese con Soporte Técnico. Error con el certificado a emitir, correspondiente a esta inspección!'))
        doc_emitido.action_generar_documento()
        if self.state != 'realizada':
            self.state = 'realizada'

    def action_pedir_supervision(self):
        self.generar_documento()
        self.estado_lista_chequeo = 'solicitar_supervisor'

    #def action_realizar(self):
    #    self.state = 'realizar'

    def action_cancel(self):
        self.state = 'cancel'

    def action_corregir(self):
        self.state = 'programada'
        self.estado_lista_chequeo = 'llenando'

    def action_aprobado_satisfactorio(self):
        self.generar_documento()
        self.estado_lista_chequeo = 'aprobado_satisfactorio'
        self.calificacion_final = 'sati'

    def action_aprobado_condicional(self):
        self.generar_documento()
        self.estado_lista_chequeo = 'aprobado_condicional'
        self.calificacion_final = 'cond'

    def action_aprobado_no_satisfactorio(self):
        self.generar_documento()
        self.estado_lista_chequeo = 'aprobado_no_satisfactorio'
        self.calificacion_final = 'nosa'


class NaveInspeccionPregunta(models.Model):
    _name = 'nave.inspeccion.pregunta'
    _description = _('Preguntas en Inspecciones de naves')
    _inherit = ['mail.thread', 'mail.activity.mixin', 'nave.inspeccion.calificacion.anulada']

    @api.model
    def selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([
            ("model", "in", ["lista.chequeo.grupo", "lista.chequeo.grupo.pregunta"])
        ])]

    inspeccion_id = fields.Many2one('nave.inspeccion', string=_('Inspección'), tracking=True)
    resource_ref = fields.Reference(string=_('Registro'), selection='selection_target_model', tracking=True)
    name = fields.Html(string=_('Texto'), tracking=True)
    display_type = fields.Selection(selection=[('line_section', _("Grupo"))], default=False, tracking=True)

    sequence_for_o2m_parent = fields.Char(string='sequence_for_o2m_parent', tracking=True)
    sequence_for_o2m_child = fields.Char(string='sequence_for_o2m_child', tracking=True)
    has_child_ids = fields.Boolean(string='has_child_ids', tracking=True)
    puntaje_no_satisfactorio = fields.Integer('Puntaje - No Satisfactorio', default=10)

    respuesta = fields.Selection(
        string=_("Respuesta"),
        selection=[
            ('sat', _("Satisfactorio")),
            ('obs', _("Observación")),
            ('nos', _("No Satisfactorio")),
            ('exe', _("Exento")),
        ],
        default=False,
        tracking=True)

    evidencia_1920 = fields.Image(
        string=_("Evidencia"),
        max_width=1920,
        max_height=1920,
        help=_("Imágen, tamaño máximo 1920x1920"))

    comentario = fields.Text(_('Comentario'))

    deficiencia_id = fields.Many2one(
        'lista.chequeo.deficiencia',
        string=_('Deficiencia'),
        ondelete='restrict')

    comentario_deficiencia = fields.Text(_('Motivos Deficiencia'))

    deficiencia_id_domain = fields.Char(
        string=_('deficiencia_id domain'),
        compute='_compute_deficiencia_id_domain',
        store=True,
        precompute=True)

    def get_domain_for_deficiencia_id(self):
        self.ensure_one()
        domain = [('id','=',-1)]
        if self.resource_ref and (self.resource_ref._name == 'lista.chequeo.grupo.pregunta'):
            domain = [('ref_normativa_id','=',False)]
            if self.resource_ref.grupo_id and self.resource_ref.grupo_id.ref_normativa_ids:
                capitulos = self.resource_ref.grupo_id.ref_normativa_ids.ids
                domain = ['|',('ref_normativa_id','=',False),('ref_normativa_cap_id.id','in',capitulos)]
        return domain

    @api.depends('resource_ref')
    def _compute_deficiencia_id_domain(self):
        for rec in self:
            domain = rec.get_domain_for_deficiencia_id()
            rec.deficiencia_id_domain = json.dumps(domain)

    def _get_respuesta_es_nos(self):
        self.ensure_one()
        return self.deficiencia_id and (
            self.deficiencia_id.anula_inspeccion or \
            self.deficiencia_id.anula_grupo or \
            self.deficiencia_id.anula_pregunta_padre or \
            self.deficiencia_id.anula_pregunta)

    def _get_respuesta_es_min_obs(self):
        self.ensure_one()
        return self.deficiencia_id and not (
            self.deficiencia_id.anula_inspeccion or \
            self.deficiencia_id.anula_grupo or \
            self.deficiencia_id.anula_pregunta_padre or \
            self.deficiencia_id.anula_pregunta)


    @api.onchange('deficiencia_id')
    def _onchange_deficiencia_id(self):
        self.ensure_one()
        if self._get_respuesta_es_nos():
            self.respuesta = 'nos'
        if not self.deficiencia_id:
            self.comentario_deficiencia = False

    @api.onchange('respuesta')
    def _onchange_respuesta(self):
        self.ensure_one()
        if self.deficiencia_id:
            if self._get_respuesta_es_nos() and self.respuesta != 'nos':
                raise UserError(_('Con la deficiencia seleccionada, la respuesta debe ser NO SATISFACTORIA'))
                self.respuesta = 'nos'
            if self._get_respuesta_es_min_obs() and (self.respuesta not in ['nos', 'obs']):
                raise UserError(_('Si selecciona una deficiencia, debe escoger la respuesta entre:\n - Observación\n - No Satisfactorio"\n\nSe recomienda que escoja Observación y escriba justificaciones en los comentarios'))
                self.respuesta = 'obs'

    def limpiar_pregunta(self):
        for rec in self:
            if not rec.display_type and not rec.has_child_ids:
                rec.evidencia_1920 = False
                rec.comentario = False
                rec.deficiencia_id = False
                rec.comentario_deficiencia = False
                rec.respuesta = False

    def get_respondida(self):
        self.ensure_one()
        if self.display_type or self.has_child_ids:
            return True
        if self.respuesta in ['sat', 'exe']:
            return True
        if self.respuesta in ['obs', 'nos'] and \
            self.deficiencia_id and self.comentario_deficiencia:
            return True
        return False

    """
    def _add_anulado_por(self, pregunta):
        self.ensure_one()
        lista = self.anulado_por.split(',')
        self.anulado_por = ','.join(lista.append(pregunta))

    def _del_anulado_por(self, pregunta):
        self.ensure_one()
        lista = self.anulado_por.split(',')
        lista_limpia = list(set(anulado_por.split(',')) - set([pregunta]))
        self.anulado_por = ','.join(lista_limpia)
    """

    def _add_del_anulados(self, add_anulado, deficiencia_obj):


        if deficiencia_obj.anula_inspeccion:
            self.inspeccion_id.add_del_anulado_por(add=add_anulado, pregunta=self.id)

        elif deficiencia_obj.anula_grupo:
            grupo_id = self.resource_ref.grupo_id.id
            grupo = self.inspeccion_id.get_grupo_from_preguntas(grupo_id)
            if grupo:
                grupo.add_del_anulado_por(add=add_anulado, pregunta=self.id)

        elif deficiencia_obj.anula_pregunta_padre:
            if self.resource_ref.parent_id:
                padre_id = self.resource_ref.parent_id.id
                padre = self.inspeccion_id.get_pregunta_from_preguntas(padre_id)
                if padre:
                    padre.add_del_anulado_por(add=add_anulado, pregunta=self.id)


    def write(self, vals):
        current_deficiencia = self.deficiencia_id
        result = super().write(vals)
        if result and ('deficiencia_id' in vals):
            if current_deficiencia and (not vals['deficiencia_id'] or current_deficiencia.id != vals['deficiencia_id']):
                # quitar los anulados por la anterior
                self._add_del_anulados(add_anulado=False, deficiencia_obj=current_deficiencia)
            if vals['deficiencia_id']:
                current_deficiencia = self.deficiencia_id
                self._add_del_anulados(add_anulado=True, deficiencia_obj=current_deficiencia)
            #import ipdb;
            #ipdb.set_trace()

        return result
