# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from cryptography.hazmat.primitives.serialization import pkcs12
import cryptography
import base64


class Company(models.Model):

    _inherit = 'res.company'

    l10n_ec_business_name = fields.Char(_('Nombre comercial'), related='partner_id.l10n_ec_business_name')
    certificate = fields.Binary('Firma electrónica')
    certificate_filename = fields.Char(string="File Name")
    certificate_password = fields.Char('Contraseña certificado', size=255)
    certificate_not_valid_before = fields.Date(string="Válido desde", compute='_compute_certificate', store=True)
    certificate_not_valid_after = fields.Date(string="Válido hasta", compute='_compute_certificate', store=True)
    certificate_issuer = fields.Char(string='Emisor certificado', compute='_compute_certificate', store=True)
    certificate_subject = fields.Char(string='Emitido certificado', compute='_compute_certificate', store=True)

    tipo_emision = fields.Selection(
        [
            ('1', 'Normal'),
            ('2', 'Indisponibilidad')
        ],
        string='Tipo de Emisión',
        required=True,
        default="1"
    )

    ambiente = fields.Selection(
        [
            ('1', 'Pruebas'),
            ('2', 'Producción')
        ],
        string='Tipo de Ambiente',
        required=True,
        default="1"
    )
    contribuyente_especial = fields.Boolean('Contribuyente especial', default=False)
    resolucion_contribuyente_especial = fields.Char('Resolución contribuyente especial', size=5)
    regimen_microempresas = fields.Boolean('Contribuyente Régimen Microempresas', default=False)


    obligado_contabilidad = fields.Boolean('Obligado a llevar contabilidad', default=True)
    resolucion_agente_retencion = fields.Char('Resolución agente retención', size=22)

    @api.constrains('certificate', 'certificate_password')
    def _check_certificate(self):
        for company in self:
            if not company.certificate or not company.certificate_password:
                continue

            try:
                _, _, _ = pkcs12.load_key_and_certificates(base64.decodebytes(company.certificate),
                                                           company.certificate_password.encode())
            except ValueError:
                raise models.ValidationError('Certificado o contraseña incorrecta')

    @api.depends('certificate', 'certificate_password')
    def _compute_certificate(self):
        for company in self:
            company.certificate_not_valid_before = None
            company.certificate_not_valid_after = None
            company.certificate_issuer = None
            company.certificate_subject = None

            if not company.certificate or not company.certificate_password:
                continue

            try:
                _, certificate, _ = pkcs12.load_key_and_certificates(base64.decodebytes(company.certificate),
                                                                     company.certificate_password.encode())
            except ValueError:
                continue

            company.certificate_not_valid_before = certificate.not_valid_before
            company.certificate_not_valid_after = certificate.not_valid_after
            company.certificate_issuer = certificate.issuer.rfc4514_string()
            company.certificate_subject = certificate.subject.rfc4514_string()
