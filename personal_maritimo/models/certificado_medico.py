from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.config import config

import requests
from lxml import etree

import logging

_logger = logging.getLogger(__name__)


class PersonalMaritimo(models.Model):
    _inherit = ['personal.maritimo']

    ficha_medica_ids = fields.One2many(
        'personal.maritimo.ficha.medica', 'personal_maritimo_id', string='Ficha Médica Persona',
        help="Ficha Médica")
    ficha_medica_count = fields.Integer(compute='_compute_ficha_medica_count')

    certificados_medicos_ids = fields.One2many(
        'personal.maritimo.ficha.medica', 'personal_maritimo_id', string='Certificado médico persona',
        help="Certificados médicos")
    certificados_medicos_count = fields.Integer(compute='_compute_certificados_medicos_count',)

    def _compute_certificados_medicos_count(self):
        for partner in self:
            partner.certificados_medicos_count = len(partner.certificados_medicos_ids)

    def _compute_ficha_medica_count(self):
        for partner in self:
            partner.ficha_medica_count = len(partner.ficha_medica_ids)

    def action_open_medical_certificates(self):
        self.ensure_one()
        return {
            'name': 'Ficha Médica',
            'type': 'ir.actions.act_window',
            'res_model': 'personal.maritimo.ficha.medica',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.ficha_medica_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id}
        }

    def _get_url_dinarp(self):
        params = self.env['ir.config_parameter'].sudo()
        url = params.get_param("personal_maritimo.dirsan_url")
        if url:
            return url
        return False

    def action_check_ficha_medica(self):
        self.ensure_one()
        try:
            url = self._get_url_dinarp()
        except Exception as e:
            print(e)

        if not self.vat:
            raise ValidationError('No existe identificación')

        data = {"cedula": self.vat}
        response = requests.post(url, data=data, timeout=3)

        root = etree.XML(response.text.encode())
        print(root.text)

        root_text = etree.fromstring(root.text)

        table = root_text.find('Table')
        if table:
            data = {
                'personal_maritimo_id': self.id,
                'centro_medica_ficha': self.env.ref('tipo_centro.dirsan').id,
            }

            if table.find('cedula'):
                data['cedula'] = table.find('cedula').text
            if table.find('FechaFact'):
                data['fecha_emision'] = table.find('FechaFact').text
                data['fecha_emision_examen_vih'] = table.find('FechaFact').text
            if table.find('FechaFact'):
                data['fecha_emision_examen_vih'] = table.find('FechaFact').text
            if table.find('prop_exam'):
                data['proposito_examen'] = table.find('prop_exam').text
            if table.find('condicion'):
                data['resultado_ficha'] = table.find('condicion').text
            if table.find('NumFac'):
                data['pnumero_factura'] = table.find('NumFac').text
            if table.find('prop_exam'):
                data['proposito_examen'] = table.find('prop_exam').text
            if table.find('condicion'):
                data['resultado_ficha'] = table.find('condicion').text
            if table.find('secuencia'):
                data['numero_ficha_aptitud'] = table.find('numero_ficha_aptitud').text
            if table.find('descripcion'):
                data['observacion'] = table.find('descripcion').text
            if table.find('numVIH'):
                data['num_vih'] = table.find('numVIH').text
            issfa = table.find('issfa').text
            nombres_todos = table.find('nombres_todos').text
            repartos = table.find('REPARTOS').text
            grados = table.find('GRADOS').text

            ficha_medica = self.env['personal.maritimo.ficha.medica'].create(data)

        return {
            'name': 'Ficha Médica',
            'type': 'ir.actions.act_window',
            'res_model': 'personal.maritimo.ficha.medica',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ficha_medica)],
            'context':  {'default_personal_maritimo_id': self.id}
        }

class CertificadoMedico(models.Model):
    _name = 'personal.maritimo.ficha.medica'
    _description = 'Ficha Médica'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(_('Description'), translate=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one(
        'res.users', string='Usuario', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    personal_maritimo_id = fields.Many2one('personal.maritimo', 'Persona de mar', tracking=True )

    centro_medico_examen = fields.Many2one('centro.medico', string='Centro Médico Examen VIH')
    country_id = fields.Many2one('res.country')

    resultado_vih = fields.Char(string='Resultado Examen VIH')
    numero_chequeo_vih = fields.Char(string='No. Chequeo VIH')
    fecha_emision_examen_vih = fields.Date(string='Fecha Emisión Examen VIH')

    numero_factura = fields.Char(string='No. Plantilla/Comprobante Ingreso')
    numero_ficha_aptitud = fields.Char(string='No. Ficha Médica')
    fecha_emision = fields.Date(string='Fecha Emisión Ficha Médica')
    fecha_caducidad = fields.Date(string='Fecha Caducidad Ficha Médica', compute='_calcular_periodo_caducidad', store=True, readonly=True)
    centro_medico_ficha = fields.Many2one('centro.medico', string='Centro Médico Ficha Médica')

    proposito_examen = fields.Char(string='Motivo de examen')
    resultado_ficha = fields.Html(string='Resultado Ficha Médica')

    caducidad = fields.Integer(string='Vigencia', default=2) #years validity
    tiempo = fields.Selection([
        ('years', 'Años'),
        ('months', 'Meses'),
    ], string='Tiempo', default='years', copy=False, tracking=True)

    observacion = fields.Html('Descrición')
    observacion_adicional = fields.Html('Observaciones adicionales')

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('vigente', 'Vigente'),
        ('caducado', 'Caducado'),
        ('cancelado', 'Cancelado')
    ], string='Estado Ficha Médica', default='borrador', index=True, copy=False, tracking=True)

    confirma_documento = fields.Boolean('Confirma Documetos?', default=False)
    audicion_satisfecha = fields.Boolean('Audicion satisfecha?', default=False)
    audicion_satisfecha_sin_audifono = fields.Boolean('Audicion satisfecha sin audifonos?', default=False)
    agudez_visual = fields.Boolean('Agudez Visual?', default=False)
    vision_cromatica = fields.Boolean('Visio cromatica?', default=False)
    apto_vigia = fields.Boolean('Apto para cometidos de vigia?', default=False)
    limitacion_fisica = fields.Boolean('Limitaciones fisica?', default=False)
    apto = fields.Boolean(string='APTO?', index=True, copy=False, tracking=True)
    fecha_vision_cromatica = fields.Date('Fecha Ultima Visión Cromática')
    restriccion = fields.Text('Detalle de limitaciones o restricciones')

    @api.depends('fecha_emision', 'tiempo', 'caducidad')
    def _calcular_periodo_caducidad(self):
        for rec in self:
            if rec.fecha_emision and rec.tiempo and rec.caducidad:
                if rec.tiempo == 'months':
                    rec.fecha_caducidad = rec.fecha_emision + relativedelta(months=+rec.caducidad)
                else:
                    rec.fecha_caducidad = rec.fecha_emision + relativedelta(years=+rec.caducidad)

    def write(self, vals):
        if vals.get('observacion'):
            self.message_post(body=_("Observaciones: %s cambió a %s", self.observacion, vals.get('observacion')))
        if vals.get('observacion_adicional'):
            self.message_post(body=_("Observaciones adicionales: %s cambió a %s", self.observacion_adicional, vals.get('observacion_adicional')))
        if vals.get('numero_ficha_aptitud'):
            vals['name'] = vals.get('numero_ficha_aptitud') + ' ' + self.personal_maritimo_id.name
        res = super().write(vals)
        return res

    def action_confirm(self):
        self.state = 'vigente'
