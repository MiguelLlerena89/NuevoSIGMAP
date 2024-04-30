from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    certificado_competencia_ids = fields.One2many(
        'permar.documento.certificado.competencia', 'personal_maritimo_id', string='Certificado Competencia',
        help="Certificados de Competencia")
    certificado_competencia_count = fields.Integer(compute='_compute_certificado_competencia_count')

    def _compute_certificado_competencia_count(self):
        for partner in self:
            partner.certificado_competencia_count = len(partner.certificado_competencia_ids)

    def action_open_certificado_competencia(self):
        self.ensure_one()
        return {
            'name': 'Certificado Competencia',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.certificado.competencia',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.certificado_competencia_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class CertificadoCompetencia(models.Model):
    _name = "permar.documento.certificado.competencia"
    _description = "Certificado competencia/suficiencia"
    _inherit = "documento.base.refrendo"

    limitacion_ids = fields.One2many("permar.documento.certificado.competencia.limitacion", "certificado_competencia_id", "Limitaciones", tracking=True)
    curso_persona_id = fields.Many2one(
        'personal.maritimo.curso',
        string='Curso Persona',
        domain="[('personal_maritimo_id', '=', personal_maritimo_id), ('estado', '=', 'vigente'),('tipo_curso', 'in', ['formacion'])]",
        index=True, tracking=True
    )
    curso_id = fields.Many2one(related='curso_persona_id.curso_id')

    tipo_jerarquia = fields.Selection(related="jerarquia_id.tipo_jerarquia")

    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'certificado.competencia')
                ]
            print(domain)
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.certificado.competencia',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)
                print('follower_id')
                print(follower_id)

    #def action_print_certificado_competencia(self):
    #    return self.env.ref('personal_maritimo_documento.action_report_certificado_competencia').report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self._get_seq_with_company("certificado_competencia_code") #self.env["ir.sequence"].next_by_code("certificado_competencia_code")
            ##vals["numero"] = self.env["ir.sequence"].next_by_code("certificado_suficiencia_code")
            doc = self.env["tramite.documento.emitido"].search([
                    ("id", "=", vals["documento_emitido_id"]),
                    ], limit=1)

            curso = self.env["personal.maritimo.curso"].search([
                    ("personal_maritimo_id", "=", doc.tramite_id.personal_maritimo_id.id),
                    ("tipo_curso", "=", 'capacitacion'),
                    ], limit=1)
            if curso:
                vals["curso_persona_id"] = curso.id
        return super().create(vals_list)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Documento persona must be unique.')
    ]

class CertificadoCompetenciaLimitacion(models.Model):
    _name = "permar.documento.certificado.competencia.limitacion"

    certificado_competencia_id = fields.Many2one(
        "permar.documento.certificado.competencia",
        string=_("Certificado Competencia/Suficiencia"),
        tracking=True)
    limitacion_id = fields.Many2one(
        "personal.maritimo.catalogo.limitacion",
        string=_("limitacion"),
        tracking=True)