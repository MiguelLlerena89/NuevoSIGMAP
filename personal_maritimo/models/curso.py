from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)


class TipoCurso(models.Model):
    _name = 'personal.maritimo.catalogo.tipo.curso'
    _description = 'Tipos de Cursos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True)
    codigo = fields.Char('Código Tipo Curso', required=True)
    descripcion = fields.Char('Descripción', required=True)
    emite_titulo = fields.Boolean('Emite titulo?', default=True)
    active = fields.Boolean(_('Active?'), default=True)
    model_id = fields.Many2one("ir.model")
    model_name = fields.Char(related="model_id.name")
    model_model = fields.Char(related="model_id.model")

    _sql_constraints = [
        ('codigo_uniq', 'unique (codigo)',
            'El código de tipo de curso ya existe!!')
    ]


class Curso(models.Model):
    _name = 'personal.maritimo.catalogo.curso'
    _description = 'Cursos'
    #_order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Descripción', required=True)
    codigo = fields.Char('Código')
    caducidad = fields.Integer(string='Años Vigencia', default=5) #years validity
    jerarquia_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string='Jerarquia', tracking=True)
    tipo_curso_id = fields.Many2one('personal.maritimo.catalogo.tipo.curso', string='Tipo Curso', tracking=True)
    tipo_curso = fields.Char(related='tipo_curso_id.codigo', string='Tipo Curso', readonly=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)
    #Reparto

    tipo = fields.Selection([
        ('capacitacion', 'Capacitación'),
        ('formacion', 'Curso Formación'),
        ('capacitacion_ext', 'Capacitación exterior'),
        ('formacion_ext', 'Curso formación exterior'),
        #('perfeccionamiento', 'Curso perfeccionamiento'),
        #('especializacion', 'Curso especialización'),
        #('ascenso', 'Curso Ascenso'),
        #('certificacion', 'Certificación'),
    ], string='Tipo', tracking=True)
    capitulo = fields.Char('Capitulo')
    regla = fields.Char('Regla')
    line_ids = fields.One2many('personal.maritimo.catalogo.curso.line', 'curso_id', string='Cursos')

    observacion = fields.Html('Observaciones')
    active = fields.Boolean(_('Active?'), default=True)

    @api.depends('name', 'line_ids')
    def name_get(self):
        result = []
        materias = ''
        for rec in self:
            if rec.tipo == 'capacitacion': #len(rec.line_ids) > 0 and
                materias = ', '.join([i.omi_id.name_get()[0][1].replace('OMI','') for i in rec.line_ids.filtered(lambda a: bool(a.omi_id) not in [False] )]) #+ ' '+ rec.capitulo + ' ' + rec.regla
            result.append((rec.id, rec.name + (f' ({materias})' if materias else '')))
                                        # ((f' ({rec.capitulo})' if rec.capitulo else '') +
                                        # (f' ({rec.regla})' if rec.regla else ''))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        if name :
            args += ['|', ('name', operator, name), ('line_ids.omi_id', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

class CursoLine(models.Model):
    _name = 'personal.maritimo.catalogo.curso.line'
    _description = 'Líneas de curso'

    curso_id = fields.Many2one('personal.maritimo.catalogo.curso', string='Curso')
    omi_id = fields.Many2one('materia.omi', string='Materia omi')
