from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

import os
import urllib
import base64
from io import BytesIO

import logging

_logger = logging.getLogger(__name__)

class PersonalMaritimo(models.Model):
    _inherit = ['personal.maritimo']

    def _prepare_foto_firma_info(self, vals):
        values = dict(
            personal_maritimo_id = vals['id'] if vals.get('id') else self.id,
            image_foto = vals['image_1920'] if vals.get('image_1920') else False,
            image_firma = vals['image_firma'] if vals.get('image_firma') else False,
            user_id = self.env.user.id,
            fecha_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            model_id = self.env['ir.model'].search([('model','=','personal.maritimo')]).id,
            model_model_id = self.id
        )
        return values

    def write(self, vals):
        if vals.get('image_1920') or vals.get('image_firma'):
            self.env['personal.maritimo.foto'].create(self._prepare_foto_firma_info(vals))
        res = super().write(vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        for partner, vals in zip(partners, vals_list):
            if vals.get('image_1920') or vals.get('image_firma'):
                vals['id'] = partner.id
                self.env['personal.maritimo.foto'].create(self._prepare_foto_firma_info(vals))
        return partners


class PersonalMaritimoFoto(models.Model):
    _name = 'personal.maritimo.foto'
    _description = 'Actualización fotos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute='_compute_name', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Usuario', index=True, tracking=True, default=lambda self: self.env.user, check_company=True)
    personal_maritimo_id = fields.Many2one('personal.maritimo', 'Persona de mar', required=True, tracking=True)
    image_foto = fields.Image('Foto Carnet', tracking=True)
    image_firma = fields.Image('Foto firma', tracking=True)
    fecha_inicio = fields.Datetime(string='Fecha inicio', index=True, tracking=True, default=fields.Datetime.now)
    modelo_partner = fields.Boolean('Es modelo partner', default= False, store=True)
    model_id = fields.Many2one("ir.model")
    model_name = fields.Char(related="model_id.name")
    model_model = fields.Char(related="model_id.model")
    model_model_id = fields.Integer(string='ID Modelo', readonly=True, store=True) #fields.Many2one(model_model, string='Modelo', store=True, tracking=True)

    @api.depends('personal_maritimo_id')
    def _compute_name(self):
        for rec in self:
            if rec.personal_maritimo_id and rec.fecha_inicio:
                rec.name = '%s - %s' % (rec.personal_maritimo_id.name, str(rec.fecha_inicio))
            else:
                rec.name = ''

    @api.onchange('personal_maritimo_id')
    def _onchange_personal_maritimo_id(self):
        for rec in self:
            if rec.personal_maritimo_id:
                rec.modelo_partner = True
            else:
                rec.modelo_partner = False

    def _synchronize_partner_values(self, vals):
        partner_values = {}
        if 'image_foto' in vals:
            partner_values['image_1920'] = vals['image_foto']
        if 'image_firma' in vals:
            partner_values['image_firma'] = vals['image_firma']
        if partner_values:
            if vals['personal_maritimo_id']:
                personal_maritimo_id = self.env['personal.maritimo'].browse(vals['personal_maritimo_id'])
                personal_maritimo_id.sudo().write(partner_values)

    # def write(self, vals):
    #     if vals.get('modelo_partner'):
    #         self._synchronize_partner_values(vals)
    #     return super().write(vals)

    # @api.model
    # def create(self, vals):
    #     if vals.get('modelo_partner'):
    #         self._synchronize_partner_values(vals)
    #     return super().create(vals)
