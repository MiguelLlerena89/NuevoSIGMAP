from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ListaChequeo(models.Model):
    _name = 'lista.chequeo'
    _description = _('Lista de chequeo')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # VERSION	NOMBRE	DESCRIPCION	ID_CERTIFICADO	FECHA_INICIO	FECHA_FIN	ESTADO

    # Nombre
    name = fields.Char(
        string=_('Nombre'),
        index=True,
        copy=True,
        tracking=True)

    version = fields.Integer(
        _('version'),
        default=1,
        required=True,
        tracking=True)

    descripcion = fields.Char(
        _('descripcion'),
        copy=True)

    fecha_ini = fields.Date(_('fecha inicio'))

    fecha_fin = fields.Date(_('fecha fin'))

    active = fields.Boolean(string=_("Activo?"), default=True,tracking=True)

    tipo_inspeccion_ids = fields.Many2many(
        'sigmap.inspector.tipo',
        'lista_chequeo_tipo_inspeccion_rel',
        'tipo_inspeccion_id',
        'lista_chequeo_id',
        required=True,
        string=_('Tipos Inspección'))

    servicio_id = fields.Many2one("tramite.documento",
        domain=lambda self: [('tipo_documento_id', '=', self.env.ref('base_sigmap.nave').id),('es_inspeccion','=',True)],
        string=_("Servicio"),
        required=False,
        tracking=True)

    tiene_condicional = fields.Boolean(string=_('tiene condicional?'), related="servicio_id.tiene_condicional")

    grupo_pregunta_ids = fields.One2many(
        'lista.chequeo.grupo',
        'lista_chequeo_id',
        string=_('Grupos'))

    pregunta_ids = fields.One2many(
        'lista.chequeo.grupo.pregunta',
        'lista_chequeo_id',
        string=_('Preguntas'))

    puntaje_max_fallo = fields.Integer(
        string=_('Puntaje Fallo (Lógica Negativa)'))

    puntaje_max = fields.Integer(
        compute='_compute_puntaje_max',
        string=_('Puntaje máximo configurado'))

    puntaje_min_satisfactorio = fields.Integer(
        string=_('Puntaje mínimo - Satisfactoria'))

    puntaje_min_condicional = fields.Integer(
        string=_('Puntaje mínimo - Condicional'))

    regla_ids = fields.One2many("nave.lista.chequeo.regla", "lista_chequeo_id", "Reglas", tracking=True)

    @api.depends('grupo_pregunta_ids', 'pregunta_ids')
    def _compute_puntaje_max(self):
        for rec in self:
            rec.puntaje_max = puntaje = 0
            for pregunta in rec.pregunta_ids:
                if not pregunta.parent_id:
                    puntaje += pregunta.puntaje_no_satisfactorio
            rec.puntaje_max = puntaje
            puntaje_min = int(puntaje * 0.7)
            if rec.puntaje_max_fallo < puntaje_min:
                rec.puntaje_max_fallo = puntaje_min

    def action_imprimir_lista_chequeo(self):
        return self.env.ref('nave_documento.action_report_nave_lista_chequeo').report_action(self)

    """
    @api.multi
    def copy(self, default=None):
        default = default or {}
        new_lista_chequeo = super(ListaChequeo, self).copy(default)
        for lista_grupo in self.grupo_pregunta_ids:
            lista_grupo.copy(default={'lista_chequeo_id': new_lista_chequeo.id})
        return new_lista_chequeo
    """


class ListaChequeoGrupoNorma(models.Model):
    _name = 'lista.chequeo.grupo.norma'
    _description = _('Lista de chequeo - Normativa')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Nombre'),
        index=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_("Activo?"),
        default=True,
        tracking=True)


class ListaChequeoGrupo(models.Model):
    _name = 'lista.chequeo.grupo'
    _description = _('Lista de chequeo - Grupo')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ID_GRUPO_LISTA	ORDEN	DESCRIPCIÓN	REFERENCIA_NORMATIVA	URL_ARCHIVO	ID_LISTA_CHEQUEO	ESTADO
    sequence = fields.Integer(default=1)

    name = fields.Char(
        string=_('Descripcion'),
        index=True,
        copy=False,
        tracking=True)

    lista_chequeo_id = fields.Many2one(
        'lista.chequeo',
        string=_('Lista Chequeo'),
        ondelete='restrict')

    ref_normativa_ids = fields.Many2many(
        comodel_name='sigmap.convenio.capitulo',
        relation='lista_chequeo_normativa_rel',
        column1='lista_chequeo_grupo_id',
        column2='convenio_capitulo_anexo_id',
        string=_('Referencia Normativa (Capítulos/Anexos)'),
        ondelete='restrict')

    active = fields.Boolean(
        string=_("Activo?"),
        default=True,
        tracking=True)

    pregunta_ids = fields.One2many(
        'lista.chequeo.grupo.pregunta',
        'grupo_id',
        string=_('Preguntas'))

    puntaje_max = fields.Integer(
        compute='_compute_puntaje_max',
        string=_('Puntaje máximo configurado'))

    @api.depends('pregunta_ids')
    def _compute_puntaje_max(self):
        for rec in self:
            rec.puntaje_max = puntaje = 0
            for pregunta in rec.pregunta_ids:
                if not pregunta.parent_id:
                    puntaje += pregunta.puntaje_no_satisfactorio
            rec.puntaje_max = puntaje

    def unlink(self):
        if self.pregunta_ids or len(self.pregunta_ids) > 0:
            raise ValidationError(_('Error al intentar eliminar. El grupo tiene preguntas asociadas. Elimine primero las preguntas'))

        res = super().unlink()
        return res

    def name_get(self):
        result = []
        for rec in self:
            rec_id = rec.id
            name = rec.name
            sequence = rec.sequence
            full_name = f'{sequence}. {name}' if sequence else f'{name}'
            result.append((rec_id, (full_name)))
        return result


class ListaChequeoDeficiencia(models.Model):
    _name = 'lista.chequeo.deficiencia'
    _description = _('Lista de chequeo - Deficiencia')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ID_DEFICIENCIA	DESCRIPCION	DESCRIPCION_INGLES	ID_DEFICIENCIA_PADRE	ID_TIPO_DEFICIENCIA	CONVENIO	CAPITULO	REGLA1	REGLA2	REGLA3	REGLA4	ESTADO
    name = fields.Char(
        string=_('Descripción'),
        index=True,
        required=True)

    name_en = fields.Char(
        string=_('Descripción (Inglés)'),
        index=True,
        required=True)

    parent_id = fields.Many2one(
        'lista.chequeo.deficiencia',
        string=_('Deficiencia Padre'),
        ondelete='restrict')


    ref_normativa_id = fields.Many2one(
        'sigmap.convenio',
        string=_('Referencia Normativa'),
        ondelete='restrict')

    ref_normativa_cap_id = fields.Many2one(
        'sigmap.convenio.capitulo',
        domain="[('convenio_id','=',ref_normativa_id)]",
        string=_('Capítulo'),
        ondelete='restrict')

    ref_normativa_regla_ids = fields.Many2many(
        'sigmap.convenio.capitulo.regla',
        'deficiencia_regla_rel',
        'deficiencia_id',
        'regla_id',
        #domain="[('regla_id.capitulo_id','=',ref_normativa_cap_id)]",
        string=_('Artículos'),
        ondelete='restrict')

    # Anula Pregunta	Anula Pregunta Padre	Anula Grupo	Anula Inspeccion
    anula_pregunta = fields.Boolean(_('Anula pregunta?'))
    porcentaje_pregunta = fields.Float(_('Porcentaje'),
        help=_('Porcentaje o factor que se aplicará para el puntaje de la pregunta, en la inspección. P.E. Si seleccionan esta deficiencia en una preguna que tiene 10 puntos y el porcentaje configurado en la deficiencia es 70%, entonces para la calificación total la pregunta sumará 7 puntos y no 10.'))
    anula_pregunta_padre = fields.Boolean(_('Anula pregunta padre?'))
    anula_grupo = fields.Boolean(_('Anula grupo?'))
    anula_inspeccion = fields.Boolean(_('Anula Inspección?'))

    @api.onchange('anula_pregunta')
    def _onchange_anula_pregunta(self):
        self.porcentaje_pregunta = 0
        if self.anula_pregunta:
            self.anula_pregunta_padre = self.anula_grupo = self.anula_inspeccion = False

    @api.onchange('anula_pregunta_padre')
    def _onchange_anula_pregunta_padre(self):
        self.porcentaje_pregunta = 0
        if self.anula_pregunta_padre:
            self.anula_pregunta = self.anula_grupo = self.anula_inspeccion = False

    @api.onchange('anula_grupo')
    def _onchange_anula_grupo(self):
        self.porcentaje_pregunta = 0
        if self.anula_grupo:
            self.anula_pregunta = self.anula_pregunta_padre = self.anula_inspeccion = False

    @api.onchange('anula_inspeccion')
    def _onchange_anula_inspeccion(self):
        self.porcentaje_pregunta = 0
        if self.anula_inspeccion:
            self.anula_pregunta = self.anula_pregunta_padre = self.anula_grupo = False


    @api.onchange('porcentaje_pregunta')
    def _onchange_porcentaje_pregunta(self):
        if self.porcentaje_pregunta and (self.anula_pregunta or self.anula_pregunta_padre or self.anula_grupo or self.anula_inspeccion):
            raise ValidationError("El porcentaje de la pregunta debe ser 0 si marca alguna de las casillas 'anula X'")

    def _vals_and_score_are_not_valid(self, vals):
        return sum([
            vals['anula_inspeccion'] if 'anula_inspeccion' in vals else self.anula_inspeccion,
            vals['anula_grupo'] if 'anula_grupo' in vals else self.anula_grupo,
            vals['anula_pregunta_padre'] if 'anula_pregunta_padre' in vals else self.anula_pregunta_padre,
            vals['anula_pregunta'] if 'anula_pregunta' in vals else self.anula_pregunta,
            bool(vals['porcentaje_pregunta']) if 'porcentaje_pregunta' in vals else bool(self.porcentaje_pregunta)
        ]) != 1

    def write(self, vals):
        if self._vals_and_score_are_not_valid(vals):
            raise ValidationError("Error en Calificación!\nMarcar una de las casillas o llenar el porcentaje/factor que aplicará a la pregunta en la inspección")
        super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if sum([
                vals['anula_inspeccion'] if 'anula_inspeccion' in vals else False,
                vals['anula_grupo'] if 'anula_grupo' in vals else False,
                vals['anula_pregunta_padre'] if 'anula_pregunta_padre' in vals else False,
                vals['anula_pregunta'] if 'anula_pregunta' in vals else False,
                bool(vals['porcentaje_pregunta']) if 'porcentaje_pregunta' in vals else False
            ]) != 1:
                raise ValidationError("Error en Calificación!\nMarcar una de las casillas o llenar el porcentaje/factor que aplicará a la pregunta en la inspección")
        return super().create(vals_list)


class ListaChequeoPregunta(models.Model):
    _name = 'lista.chequeo.grupo.pregunta'
    _description = _('Lista de chequeo - Pregunta')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence_for_o2m_order'

    sequence = fields.Integer(default=1)

    name = fields.Char(
        string=_('Texto Corto'),
        index=True,
        copy=False,
        tracking=True)

    texto = fields.Html('Texto Adicional')

    '''
    parent_name = fields.Char(
        string=_('Compuesta'),
        index=True,
        copy=False,
        tracking=True)
    '''

    lista_chequeo_id = fields.Many2one(
        'lista.chequeo',
        string=_('Lista Chequeo'),
        ondelete='restrict')

    grupo_id = fields.Many2one(
        'lista.chequeo.grupo',
        string=_('Grupo'),
        ondelete='restrict')

    is_parent = fields.Boolean(
        string=_('Es parte de otra?'),
        default=False)

    parent_id = fields.Many2one(
        'lista.chequeo.grupo.pregunta',
        string=_('Principal'),
        ondelete='restrict')

    child_ids = fields.One2many(
        'lista.chequeo.grupo.pregunta',
        'parent_id',
        string=_('Hijos'))

    puntaje_no_satisfactorio = fields.Integer('Puntaje')

    porcentaje_si_hijo = fields.Float('Porcentaje')

    '''
    display_type = fields.Selection(
        selection=[
            ('hijo', _('Hijo')),
            ('padre', _('Padre')),
        ],
        default='hijo',
        string='Tipo Seccion'
    )
    '''
    sequence_for_o2m_order = fields.Char(compute='_compute_sequence_for_o2m', string='sequence_for_o2m_order', store=True)
    sequence_for_o2m_parent = fields.Char(compute='_compute_sequence_for_o2m', string='sequence_for_o2m_parent')
    sequence_for_o2m_child = fields.Char(compute='_compute_sequence_for_o2m', string='sequence_for_o2m_child')
    porcentaje_for_o2m_child = fields.Char(compute='_compute_sequence_for_o2m', string='porcentaje_for_o2m_child')
    puntaje_for_o2m_parent = fields.Char(compute='_compute_sequence_for_o2m', string='puntaje_for_o2m_parent')
    has_child_ids = fields.Boolean(compute='_compute_sequence_for_o2m', string='has_child_ids')

    @api.depends('child_ids', 'is_parent', 'parent_id', 'sequence')
    def _compute_sequence_for_o2m(self):
        for rec in self:
            rec.sequence_for_o2m_order = rec.sequence_for_o2m_parent = rec.sequence_for_o2m_child = ""
            rec.porcentaje_for_o2m_child = rec.puntaje_for_o2m_parent = ""
            order = str(rec.sequence)
            if rec.is_parent and rec.parent_id:
                parent_order = str(rec.parent_id.sequence)
                rec.sequence_for_o2m_order = parent_order.zfill(4) + "." + order.zfill(4) + "."
                rec.sequence_for_o2m_parent = ""
                rec.sequence_for_o2m_child = order
                rec.porcentaje_for_o2m_child = str(int(rec.porcentaje_si_hijo * 100)) + "%"
                rec.puntaje_for_o2m_parent = ""
            else:
                rec.sequence_for_o2m_order = order.zfill(4) + "."
                rec.sequence_for_o2m_parent = order
                rec.sequence_for_o2m_child = ""
                rec.porcentaje_for_o2m_child = ""
                rec.puntaje_for_o2m_parent = str(rec.puntaje_no_satisfactorio)

            rec.has_child_ids = len(rec.child_ids) > 0


    def unlink(self):
        if self.child_ids or len(self.child_ids) > 0:
            raise ValidationError(_('Error al intentar eliminar. La pregunta es compuesta y tiene sub-preguntas asociadas. Elimine primero las sub-preguntas'))

        res = super().unlink()
        return res

    def name_get(self):
        result = []
        for rec in self:
            rec_id = rec.id
            name = rec.name
            sequence = rec.sequence
            full_name = f'{sequence}. {name}' if sequence else f'{name}'
            result.append((rec_id, (full_name)))
        return result

    def get_puntaje_for_respuesta(self):
        self.ensure_one()
        puntaje = 10
        if self.parent_id and self.parent_id.puntaje_no_satisfactorio > 0 and self.porcentaje_si_hijo:
            puntaje = self.porcentaje_si_hijo * self.parent_id.puntaje_no_satisfactorio
        if not self.parent_id and self.puntaje_no_satisfactorio > 0:
            puntaje = self.puntaje_no_satisfactorio
        return puntaje

class NaveListaAutorizadaRegla(models.Model):
    _name = 'nave.lista.chequeo.regla'
    _description = _('Regla - lista chequeo de naves')
    _inherit = ['nave.domain.regla', 'mail.thread', 'mail.activity.mixin']
    _or_values_field = "regla_or_ids"

    lista_chequeo_id = fields.Many2one("lista.chequeo", "Lista Chequeo")
    regla_or_ids = fields.One2many("nave.lista.chequeo.regla.or", "lista_chequeo_regla_id", "Opciones", tracking=True)


class NaveListaAutorizadaReglaOr(models.Model):
    _name = 'nave.lista.chequeo.regla.or'
    _description = _('Regla Opciones - lista chequeo de naves')
    _inherit = ['nave.domain.regla.or', 'mail.thread', 'mail.activity.mixin']
    _rule_parent_field = "lista_chequeo_regla_id"

    lista_chequeo_regla_id = fields.Many2one("nave.lista.chequeo.regla", "Lista Chequeo - Regla")
    regla_variable = fields.Selection(
        related="lista_chequeo_regla_id.variable", string=_("Variable"), tracking=True)


class ListaChequeoInspeccion(models.Model):
    _name = 'lista.chequeo.inspeccion'
    _description = _('Lista de chequeo - Inspección')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(default=1)

    name = fields.Char(
        string=_('Descripcion'),
        index=True,
        copy=False,
        tracking=True)

    # usuario_inspector
    # lista_chequeo_id
    # fecha_inspeccion
    # se_supervisa
    # usuario_supervisor
    # fecha_supervision
    # respuestas_ids

class ListaChequeoInspeccionRespuesta(models.Model):
    _name = 'lista.chequeo.inspeccion.respuesta'
    _description = _('Lista de chequeo - Respuesta')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(default=1)

    name = fields.Char(
        string=_('Descripcion'),
        index=True,
        copy=False,
        tracking=True)

    # pregunta
    # respuesta
    # imágen
    # observaciones
    # deficiencia
    # accion
    # score
