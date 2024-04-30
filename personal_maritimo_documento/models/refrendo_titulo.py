from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = ['personal.maritimo']

    refrendo_titulo_ids = fields.One2many(
        'permar.documento.refrendo.titulo.formacion', 'personal_maritimo_id', string='Refrendo de Titulos',
        help="Refrendo de titulos asociados a personal maritimo")
    refrendo_titulo_count = fields.Integer(compute='_compute_refrendo_titulo_count')

    def _compute_refrendo_titulo_count(self):
        for partner in self:
            partner.refrendo_titulo_count = len(partner.refrendo_titulo_ids)

    def action_open_refrendo_titulo(self):
        self.ensure_one()
        return {
            'name': 'Refrendo de Títulos',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.refrendo.titulo.formacion',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.refrendo_titulo_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class RefrendoTituloFormacion(models.Model):
    _name = "permar.documento.refrendo.titulo.formacion"
    _description = "Refrendo titulo formacion"
    _inherit = "documento.base.refrendo"

    curso_persona_id = fields.Many2one(
        "personal.maritimo.curso",
        string=_("Curso"),
        domain="[('personal_maritimo_id', '=', personal_maritimo_id), ('estado', '=', 'vigente'),('tipo_curso', 'in', ['formacion'])]",
        tracking=True)
    curso_id = fields.Many2one(related='curso_persona_id.curso_id')
    #reparto = fields.Char(string=_("Reparto"), size=100, index=True, tracking=True)
    limitacion_ids = fields.One2many("permar.documento.refrendo.limitacion", "refrendo_id", "Limitaciones", tracking=True)

    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'permar.documento.refrendo.titulo.formacion')
                ]
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.refrendo.titulo.formacion',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)
                print('follower_id')
                print(follower_id)

    def write(self, vals):
        res = super().write(vals)
        #self._add_followers()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" not in vals:
                vals["name"] = self._get_seq_with_company("titulo_folio_code") #self.env["ir.sequence"].next_by_code("titulo_folio_code")

            params = self.env['ir.config_parameter'].sudo()

            libro=params.get_param("tramite.libro_numero")

            vals["numero"] = self._get_seq_with_company("refrendo_titulo_code") #self.env["ir.sequence"].next_by_code("refrendo_titulo_code")

            doc = self.env["tramite.documento.emitido"].search([
                    ("id", "=", vals["documento_emitido_id"]),
                    ], limit=1)

            for requisito in doc.tramite_id.requisito_ids:
                curso = self.env["personal.maritimo.curso"].search([
                        ("personal_maritimo_id", "=", doc.tramite_id.personal_maritimo_id.id),
                        ("tipo_curso", "=", 'formacion'),
                        ("jerarquia_id", "=", requisito.tramite_id.jerarquia_id.id),
                        ], limit=1)
                if curso:
                    vals["curso_persona_id"] = curso.id
        return super().create(vals_list)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Documento persona must be unique.')
    ]


class RefrendoLimitacion(models.Model):
    _name = "permar.documento.refrendo.limitacion"

    refrendo_id = fields.Many2one(
        "permar.documento.refrendo.titulo.formacion",
        string=_("Refrendo título"),
        tracking=True)
    limitacion_id = fields.Many2one(
        "personal.maritimo.catalogo.limitacion",
        string=_("limitacion"),
        tracking=True)