from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import time
import calendar
import datetime
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = ['personal.maritimo']

    refrendo_medico_ids = fields.One2many(
        'permar.documento.refrendo.certificado.medico', 'personal_maritimo_id', string='Refrendo Médico',
        help="Refrendo de Certificado Medico")
    refrendo_medico_count = fields.Integer(compute='_compute_refrendo_medico_count')

    def _compute_refrendo_medico_count(self):
        for partner in self:
            partner.refrendo_medico_count = len(partner.refrendo_medico_ids)

    def action_open_refrendo_medico(self):
        self.ensure_one()
        return {
            'name': 'Refrendo Médico',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.refrendo.certificado.medico',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.refrendo_medico_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class RefrendoCertificadoMedico(models.Model):
    _name = "permar.documento.refrendo.certificado.medico"
    _description = "Refrendo Certificado Médico"
    _inherit = "documento.base"

    ficha_medica_id = fields.Many2one(
        "personal.maritimo.ficha.medica",
        string=_("Ficha Médica"),
        domain="[('personal_maritimo_id', '=', personal_maritimo_id), ('state', '=', 'vigente'), ('company_id', '=', company_id)]",
        tracking=True)

    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'permar.documento.refrendo.certificado.medico')
                ]
            print(domain)
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.refrendo.certificado.medico',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self._get_seq_with_company("certificado_medico_code") #self.env["ir.sequence"].next_by_code("certificado_medico_code")
            #vals["numero"] = self.env["ir.sequence"].next_by_code("certificado_print_medico_code")
            # Check for available certificado médico
            print(vals)
            doc = self.env["tramite.documento.emitido"].search([
                    ("id", "=", vals["documento_emitido_id"]),
                    ], limit=1)
            params = self.env['ir.config_parameter'].sudo()
            tiempo_minimo_validez_documentos=params.get_param("tramite.tiempo_minimo_validez_documentos")
            fecha_maxima = fields.Date.today() + relativedelta(months=int(tiempo_minimo_validez_documentos))
            ficha_medica = self.env["personal.maritimo.ficha.medica"].search([
                    ("personal_maritimo_id", "=", doc.tramite_id.personal_maritimo_id.id),
                    ("fecha_caducidad", ">", fecha_maxima)
                    ], limit=1)
            if ficha_medica:
                vals["ficha_medica_id"] = ficha_medica.id
        return super().create(vals_list)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Documento persona must be unique.')
    ]


class CertificadoMedico(models.Model):
    _inherit = "personal.maritimo.ficha.medica"

    @api.model
    def validar_como_requerido(self, **kwargs):
        beneficiario = kwargs['personal_maritimo_id']
        model = self._name
        doc = False
        params = self.env['ir.config_parameter'].sudo()
        tiempo_minimo_validez_documentos = params.get_param("tramite.tiempo_minimo_validez_documentos")
        fecha_tope = date.today() + relativedelta(months=int(tiempo_minimo_validez_documentos))
        data = [
            ("personal_maritimo_id", "=", beneficiario.id),
            ("fecha_caducidad", ">=", fecha_tope),
            ("state", "=", 'vigente')
        ]
        doc = self.env[model].search(data, limit=1)
        return doc, bool(doc)
