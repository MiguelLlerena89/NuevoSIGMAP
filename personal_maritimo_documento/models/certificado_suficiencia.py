from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    certificado_suficiencia_ids = fields.One2many(
        'permar.documento.certificado.suficiencia', 'personal_maritimo_id', string='Certificado Suficiencia',
        help="Certificados de Suficiencia")
    certificado_suficiencia_count = fields.Integer(compute='_compute_certificado_suficiencia_count')

    def _compute_certificado_suficiencia_count(self):
        for partner in self:
            partner.certificado_suficiencia_count = len(partner.certificado_suficiencia_ids)

    def action_open_certificado_suficiencia(self):
        self.ensure_one()
        return {
            'name': 'Certificado Suficiencia',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.certificado.suficiencia',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.certificado_suficiencia_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }

class CertificadoSuficiencia(models.Model):
    _name = "permar.documento.certificado.suficiencia"
    _description = "Certificado suficiencia OMI"
    _inherit = "documento.base.refrendo"

    curso_persona_id = fields.Many2one(
        'personal.maritimo.curso',
        string='Curso Persona',
        domain="[('personal_maritimo_id', '=', personal_maritimo_id), ('estado', '=', 'vigente'),('tipo_curso', 'in', ['capacitacion'])]",
        index=True, tracking=True
    )

    limitacion_ids = fields.One2many("permar.documento.certificado.suficiencia.limitacion", "certificado_suficiencia_id", "Limitaciones", tracking=True)

    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'permar.documento.certificado.suficiencia')
                ]
            print(domain)
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.certificado.suficiencia',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)
                print('follower_id')
                print(follower_id)

    #def action_print_certificado_suficiencia(self):
    #    return self.env.ref('personal_maritimo_documento.action_report_certificado_suficiencia').report_action(self)

    # def action_print_libretin_certificado_suficiencia(self):
    #     return self.env.ref('personal_maritimo_documento.action_report_libretin_certificado_suficiencia').report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self._get_seq_with_company("certificado_suficiencia_code") #self.env["ir.sequence"].next_by_code("certificado_suficiencia_code")
            doc = self.env["tramite.documento.emitido"].search([
                    ("id", "=", vals["documento_emitido_id"]),
                    ], limit=1)

            curso = self.env["personal.maritimo.curso"].search([
                    ("personal_maritimo_id", "=", doc.tramite_id.personal_maritimo_id.id),
                    ("curso_id", "=", doc.tramite_id.curso_id.id),
                    ], limit=1)
            if curso:
                vals["curso_persona_id"] = curso.id
        return super().create(vals_list)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Certificado de Suficiencia debe ser único.')
    ]

class CertificadoSuficienciaLimitacion(models.Model):
    _name = "permar.documento.certificado.suficiencia.limitacion"

    certificado_suficiencia_id = fields.Many2one(
        "permar.documento.certificado.suficiencia",
        string=_("Certificado Suficiencia"),
        tracking=True)
    limitacion_id = fields.Many2one(
        "personal.maritimo.catalogo.limitacion",
        string=_("limitacion"),
        tracking=True)