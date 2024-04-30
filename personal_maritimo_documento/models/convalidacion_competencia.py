from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    convalidacion_competencia_ids = fields.One2many(
        'permar.documento.convalidacion.competencia', 'personal_maritimo_id', string='Convalidación de Competencia',
        help="Convalidación de Competencia")
    convalidacion_competencia_count = fields.Integer(compute='_compute_convalidacion_competencia_count')

    def _compute_convalidacion_competencia_count(self):
        for partner in self:
            partner.convalidacion_competencia_count = len(partner.convalidacion_competencia_ids)

    def action_open_convalidacion_competencia(self):
        self.ensure_one()
        return {
            'name': 'Convalidación de Competencia',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.convalidacion.competencia',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.convalidacion_competencia_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class ConvalidacionCompetencia(models.Model):
    _name = 'permar.documento.convalidacion.competencia'
    _description = 'Convalidación Competencia'
    _inherit = "documento.base"

    especialidad = fields.Char(string=_("Especialidad"), size=100, index=True, tracking=True)
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

    @api.model
    def create(self, vals):
        vals["name"] = self._get_seq_with_company("convalidacion_competencia_code") #self.env["ir.sequence"].next_by_code("convalidacion_competencia_code")
        #vals["numero"] = self.env["ir.sequence"].next_by_code("convalidacion_competencia_code")
        return super(ConvalidacionCompetencia, self).create(vals)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Documento de convalidación ya existe!"),
    ]
