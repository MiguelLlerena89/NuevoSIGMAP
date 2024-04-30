from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class PersonalMaritimo(models.Model):
    _inherit = ['personal.maritimo']

    cursos_ids = fields.One2many(
        'personal.maritimo.curso', 'personal_maritimo_id', string='Cursos de personal marítimo',
        help="Cursos de personal marítimo")
    cursos_count = fields.Integer(compute='_compute_cursos_count')

    def _compute_cursos_count(self):
        for partner in self:
            partner.cursos_count = len(partner.cursos_ids)

    def action_open_courses(self):
        self.ensure_one()
        return {
            'name': 'Cursos de personal marítimo',
            'type': 'ir.actions.act_window',
            'res_model': 'personal.maritimo.curso',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.cursos_ids.ids)],
            'context': {'search_default_group_tipo': '1', 'default_personal_maritimo_id': self.id}
            }


class PersonaMaritimaCurso(models.Model):
    _name = 'personal.maritimo.curso'
    _description = 'Cursos de personal marítimo'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    personal_maritimo_id = fields.Many2one('personal.maritimo', 'Persona de mar', tracking=True, required=True)
    fecha_inicio = fields.Date(string='Fecha Inicio', index=True, copy=False)
    fecha_termino = fields.Date(string='Fecha Término')
    fecha_caducidad = fields.Date('Fecha Caducidad', compute="_calcular_periodo_caducidad", store=True, readonly=True)
    name = fields.Char(string='Nombre', index=True, copy=False, tracking=True)
    numero_diploma = fields.Char(string='Número del Diploma', index=True, copy=False, tracking=True)
    numero_formulario = fields.Char(string='Número especie', tracking=True)
    fecha_emision_diploma = fields.Date(string='Fecha Emisión Diploma', index=True, copy=False, tracking=True)

    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('vigente', 'Vigente'),
        ('caducado', 'Caducado'),
        ('cancelado', 'Cancelado')
    ], string='Estado de curso relacioando a persona', default='vigente', index=True, copy=False, tracking=True)

    observacion = fields.Html('Observaciones')
    user_id = fields.Many2one('res.users', 'User', store=True, readonly=False)
    #active = fields.Boolean(_('Active?'), default=True)

    curso_id = fields.Many2one('personal.maritimo.catalogo.curso', 'Curso', required=True, index=True, copy=False, tracking=True)
    jerarquia_id = fields.Many2one(related='curso_id.jerarquia_id', store=True)
    codigo = fields.Char(related='curso_id.codigo', string='Código Curso', readonly=True)
    tipo_curso = fields.Selection(related='curso_id.tipo', string='Tipo', store=True)
    #tipo_curso_id = fields.Many2one('personal.maritimo.catalogo.tipo.curso', string='Tipo Curso')
    tipo_curso_id = fields.Many2one(related='curso_id.tipo_curso_id', string='Tipo Curso',store=True)
    caducidad = fields.Integer(related='curso_id.caducidad', string='Años Vigencia', readonly=True)
    country_id = fields.Many2one('res.country', string='País Realización', index=True, copy=False, tracking=True)
    lugar_formacion_id = fields.Many2one('lugar.formacion', string='Lugar Realización', domain="[('centro_id','=',centro_formacion_id)]", index=True, copy=False, tracking=True)
    #Reparto
    centro_formacion_id = fields.Many2one('centro.formacion',  string='Centro Realización', index=True, copy=False, tracking=True)
    tipo_formacion_id = fields.Many2one('personal.maritimo.curso.tipo.formacion', 'Tipo formación', index=True, copy=False, tracking=True)

    es_omi = fields.Boolean(string='OMI?', compute="_compute_omi", index=True, readonly=True)
    es_reconocimiento = fields.Boolean(string='Es reconocimiento?', index=True, tracking=True)
    es_evaluacion = fields.Boolean(string='Es evaluación?', index=True, tracking=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)

    @api.depends('curso_id')
    def _compute_omi(self):
        for rec in self:
            rec.es_omi = True if rec.curso_id.tipo == 'capacitacion' else False

    @api.depends('fecha_termino', 'caducidad')
    def _calcular_periodo_caducidad(self):
        for rec in self:
            if rec.fecha_termino and rec.caducidad and rec.tipo_curso not in ['formacion', 'formacion_ext']:
                rec.fecha_caducidad = rec.fecha_termino + relativedelta(years=+rec.caducidad)

    @api.model_create_multi
    def create(self, vals_list):
        cursos = self.browse()
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("curso_persona_code")
            cursos |= super().create(vals)
        for curso in cursos:
            jerarquias = curso.personal_maritimo_id.jerarquia_ids.filtered(lambda c: c.active)
            for j in jerarquias:
                j.active = False
            if curso.tipo_curso == "formacion":
                params = self.env['ir.config_parameter'].sudo()

                dias_disponibles_provisional=params.get_param("personal_maritimo.dias_disponibles_permiso_provisional")
                dias_disponibles_dispensa=params.get_param("personal_maritimo.dias_disponibles_dispensa")
                # Asignar nuevos días disponibles para permisos
                data = {
                    'jerarquia_id': curso.jerarquia_id.id,
                    'folio_acta': curso.name,
                    'curso_id': curso.id,
                    'dias_disponibles_provisional': int(dias_disponibles_provisional),
                    'dias_disponibles_dispensa': int(dias_disponibles_dispensa),
                    'active': True
                }
                curso.personal_maritimo_id.write({'jerarquia_ids': [(0,0,data)]})

        return cursos


class PersonalMaritimoCursoTipoFormacion(models.Model):
    _name = 'personal.maritimo.curso.tipo.formacion'
    _description = 'Tipos de formación'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True)
    codigo = fields.Char('Código', required=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)
