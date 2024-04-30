from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from dateutil.relativedelta import relativedelta

import os
import urllib
import base64
from io import BytesIO

import logging

_logger = logging.getLogger(__name__)


class TipoInfraccion(models.Model):
    _name = 'tipo.infraccion'
    _description = 'Tipo de Infraccion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True)
    active = fields.Boolean(_('Active?'), default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'El tipo de infracción ya existe!!')
    ]


class TipoSancion(models.Model):
    _name = 'tipo.sancion'
    _description = 'Tipo de Sancion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True)
    active = fields.Boolean(_('Active?'), default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            'El tipo de sanción ya existe!!')
    ]


class PersonalMaritimo(models.Model):
    _inherit = ['personal.maritimo']

    sancion_ids = fields.One2many(
        'personal.maritimo.sancion', 'personal_maritimo_id', string='Sancion persona')
    sanciones_count = fields.Integer(compute='_compute_sanciones_count')
    sancion_activa = fields.Boolean(compute='_compute_sancion_activa', tracking=True)

    def _compute_sancion_activa(self):
        for partner in self:
            sancion_activa = partner.sancion_ids.filtered(lambda c: c.estado not in ('pendiente','finalizado'))
            if len(list(sancion_activa)) > 0:
                partner.sancion_activa = True
            else:
                partner.sancion_activa = False

    def _compute_sanciones_count(self):
        for partner in self:
            partner.sanciones_count = len(partner.sancion_ids)

    def action_open_sanction(self):
        self.ensure_one()
        return {
            'name': 'Sanciones',
            'type': 'ir.actions.act_window',
            'res_model': 'personal.maritimo.sancion',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.sancion_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id}
        }

class PersonaMaritimaSancion(models.Model):
    _name = 'personal.maritimo.sancion'
    _description = 'Sancion a personal maritimo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Descripción', required=True)
    personal_maritimo_id = fields.Many2one('personal.maritimo', 'Persona de mar', tracking=True )
    tipo = fields.Selection([
        ('persona', 'Persona'),
        ('jerarquia', 'Jerarquía'),
        ('matricula', 'Matrícula'),
    ], string='Tipo', required=True, tracking=True)
    tipo_infraccion_id = fields.Many2one('tipo.infraccion', string='Tipo de Infracción', required=True, tracking=True)
    tipo_sancion_id = fields.Many2one('tipo.sancion', string='Tipo de Sancion', tracking=True)

    #Reparto
    dias = fields.Integer('# Días', default=0)
    valor = fields.Float('Valor')

    fecha_falta = fields.Date(string='Fecha Falta', index=True, copy=False, tracking=True) #Fecha Emision de la Sancion
    fecha_inicio = fields.Date(string='Fecha Inicio', index=True, copy=False, tracking=True)
    fecha_fin = fields.Date(string='Fecha Fin', index=True, copy=False, tracking=True)

    motivo_sancion = fields.Html('Motivo de sanción')
    observacion_sancion = fields.Html('Observaciones de sanción')
    referencia_sancion = fields.Html('Referencia de sanción')

    numero_documento = fields.Char('No. Documento Resolución')
    motivo_finalizacion = fields.Html('Motivo de finalización de sanción')
    observacion_finalizacion = fields.Html('Observaciones de finalización de sanción')
    referencia_finalizacion = fields.Html('Referencia de finalización de sanción')
    pdf_file = fields.Binary(string='Archivo Resolución')
    pdf_filename = fields.Char(string='Nombre Resolución', size=60)

    estado = fields.Selection([
        ('pendiente', 'Pendiente'),
        ('citacion', 'En Citación'),
        ('sancionado', 'Sancionado'),
        ('finalizado', 'Finalizado'),
    ], string='Estado de sanción a persona', default='pendiente', index=True, copy=False, tracking=True)
    #active = fields.Boolean(_('Active?'), default=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Usuario', index=True, tracking=True, default=lambda self: self.env.user, check_company=True)

    @api.depends('fecha_inicio', 'dias')
    def _calcular_periodo_sancion(self):
        for rec in self:
            if rec.fecha_inicio and rec.dias:
                rec.fecha_fin = rec.fecha_inicio + relativedelta(years=+rec.dias)

