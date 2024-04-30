from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    evaluacion_competencia_ids = fields.One2many(
        'permar.documento.convalidacion.competencia', 'personal_maritimo_id', string='Evaluación de Competencia',
        help="Evaluación de Competencia")
    evaluacion_competencia_count = fields.Integer(compute='_compute_evaluacion_competencia_count')

    def _compute_evaluacion_competencia_count(self):
        for partner in self:
            partner.evaluacion_competencia_count = len(partner.evaluacion_competencia_ids)

    def action_open_evaluacion_competencia(self):
        self.ensure_one()
        return {
            'name': 'Evaluación de Competencia',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.convalidacion.competencia',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.evaluacion_competencia_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }

class EvaluacionCompetencia(models.Model):
    _name = 'permar.documento.evaluacion.competencia'
    _description = 'Evaluación Competencia'
    _inherit = "documento.base"

    jerarquia_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string='Especialidad', tracking=True)
    #reparto = fields.Char(string=_("Reparto"), size=100, index=True, tracking=True)
    observacion = fields.Html('Observaciones')

    documento_evaluacion_id = fields.Many2one('permar.documento.evaluacion', 'Documento Evaluación')
    numero_oficio = fields.Char(related='documento_evaluacion_id.numero_oficio', string="Número de oficio", store=True, readonly=False)
    antecedente = fields.Text(related='documento_evaluacion_id.antecedente', store=True, readonly=False)
    analisis = fields.Text(related='documento_evaluacion_id.analisis', store=True, readonly=False)
    conclusion = fields.Text(related='documento_evaluacion_id.conclusion', store=True, readonly=False)
    recomendacion = fields.Text(related='documento_evaluacion_id.recomendacion', store=True, readonly=False)
    fecha_informe = fields.Date(related='documento_evaluacion_id.fecha_informe', store=True, readonly=False)
    centro_formacion_id = fields.Many2one(related='documento_evaluacion_id.centro_formacion_id', string='Centro Realización', index=True, copy=False, tracking=True, store=True, readonly=False)
    active = fields.Boolean(related='documento_evaluacion_id.active', default=True)

    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'permar.documento.convalidacion.competencia')
                ]
            print(domain)
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.convalidacion.competencia',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)
                print('follower_id')
                print(follower_id)

    @api.model
    def create(self, vals):
        vals["name"] = self._get_seq_with_company("evaluacion_competencia_code") #self.env["ir.sequence"].next_by_code("evaluacion_competencia_code")
        #vals["numero"] = self.env["ir.sequence"].next_by_code("evaluacion_competencia_code")
        return super(EvaluacionCompetencia, self).create(vals)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Documento de evaluación ya existe!"),
    ]
