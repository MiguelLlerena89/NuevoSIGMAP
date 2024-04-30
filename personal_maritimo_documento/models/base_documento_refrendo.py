from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class DocumentoRefrendosBase(models.Model):
    _inherit = "documento.base"
    _name = "documento.base.refrendo"
    _description = "Documentos refrendos base"

    fecha_emision_diploma = fields.Date(
        string='Fecha emisión diploma',
        index=True,
        copy=False,
        tracking=True)

    curso_id = fields.Many2one(
        'personal.maritimo.catalogo.curso',
        string='Curso',
        index=True, tracking=True)
    curso_persona_id = fields.Many2one(
        'personal.maritimo.curso',
        string='Curso Persona',
        index=True, tracking=True)
    jerarquia_id = fields.Many2one("personal.maritimo.catalogo.jerarquia", string=_("Jerarquía"), tracking=True, store=True)
    tipo_formacion = fields.Selection(related='curso_persona_id.tipo_curso')
    curso_name = fields.Char(related='curso_persona_id.curso_id.name', string='Nombre Curso', index=True, copy=False, tracking=True)
    fecha_inicio_curso = fields.Date(related='curso_persona_id.fecha_inicio', string='Fecha Inicio Curso', index=True, copy=False, tracking=True)
    fecha_termino = fields.Date(related='curso_persona_id.fecha_termino', string='Fecha Termino Curso', index=True, copy=False, tracking=True)

    numero_diploma = fields.Char(related='curso_persona_id.numero_diploma', string='Número del Diploma', index=True, copy=False, tracking=True)
    numero_formulario = fields.Char(related='curso_persona_id.numero_formulario', string='Número del Formulario', tracking=True)
    fecha_emision_diploma = fields.Date(related='curso_persona_id.fecha_emision_diploma', string='Fecha Emisión Diploma', index=True, copy=False, tracking=True)
    centro_formacion_id = fields.Many2one(related='curso_persona_id.centro_formacion_id', string='Centro Formación', tracking=True, store=True)
    lugar_formacion_id = fields.Many2one(related='curso_persona_id.lugar_formacion_id', string='Lugar Formación', index=True, tracking=True)
    limitacion_id = fields.Many2one(
        "personal.maritimo.catalogo.limitacion",
        string=_("limitacion"),
        compute="_compute_get_limitacion",
        store=True,
        tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if 'documento_emitido_id' in vals:
                documento_emitido_id = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
                if 'curso_id' in vals:
                    curso = self.env['personal.maritimo.curso'].search([
                        ("personal_maritimo_id", "=", documento_emitido_id.personal_maritimo_id.id ),
                        ("curso_id", "=", vals['curso_id'] ),
                        ], limit=1)
                    if curso:
                        vals['curso_persona_id'] = curso.id
                        if curso.jerarquia_id:
                            vals['jerarquia_id'] = curso.jerarquia_id.id
                        else:
                            vals['jerarquia_id'] = documento_emitido_id.personal_maritimo_id.jerarquia_id.id
        return super().create(vals_list)

    @api.depends('jerarquia_id')
    def _compute_get_limitacion(self):
        self.limitacion_id = False
        jerarquia_activa = self.personal_maritimo_id.jerarquia_ids.filtered(lambda l: l.active)
        if jerarquia_activa:
            self.limitacion_id = jerarquia_activa.limitacion_id

    @api.model
    def validar_como_requerido(self, **kwargs):
        beneficiario = kwargs['personal_maritimo_id']
        model = self._name
        curso_id = kwargs['curso_id']
        jerarquia_id = kwargs['jerarquia_id']
        doc = False
        data = [
            ("personal_maritimo_id", "=", beneficiario.id),
            ("state", "=", 'vigente')
        ]

        cursos_requeridos_ids = jerarquia_id.requisito_ids.mapped('curso_id').ids

        if 'permar.documento.refrendo.titulo.formacion' in model:
            cursos_requeridos_ids = [curso_id.id]

        data.append(
            ('curso_id', 'in', cursos_requeridos_ids),
        )

        certificados_ids = self.env[model].search(data)

        cursos_certificados = certificados_ids.mapped('curso_id').ids

        if len(set(cursos_requeridos_ids) - set(cursos_certificados)) > 0:
            return False, False
        class Object(object):
            pass

        doc = Object()
        doc.id = None
        doc.name = "Cursos completados"
        doc.fecha_caducidad = None
        #doc.fecha_caducidad = "Menor fecha entre todos los certificados"

        return doc, True

class PersonalMaritimoCurso(models.Model):
    _inherit = "personal.maritimo.curso"

    @api.model
    def validar_como_requerido(self, **kwargs):
        beneficiario = kwargs['personal_maritimo_id']
        model = self._name
        curso_id = kwargs['curso_id']
        doc = False
        data = [
            ("personal_maritimo_id", "=", beneficiario.id),
            ("curso_id", "=", curso_id.id),
            #("state", "=", 'vigente')
        ]
        doc = self.env[model].search(data, limit=1)
        return doc, bool(doc)

#class TipoCurso(models.Model):
#    _inherit = 'personal.maritimo.catalogo.tipo.curso'
