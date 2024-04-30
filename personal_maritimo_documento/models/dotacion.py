from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    dotacion_ids = fields.One2many(
        'permar.documento.dotacion', 'personal_maritimo_id', string='Dotación',
        help="Dotaciones asociados a personal maritimo")
    dotacion_count = fields.Integer(compute='_compute_dotacion_count')

    def _compute_dotacion_count(self):
        for partner in self:
            partner.dotacion_count = len(partner.dotacion_ids)

    def action_open_dotacion(self):
        self.ensure_one()
        return {
            'name': 'Dotación',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.dotacion',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.dotacion_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class Dotacion(models.Model):
    _name = "permar.documento.dotacion"
    _description = "Dotación"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _inherit = "documento.base"

    observacion = fields.Html('Observaciones')

    @api.model
    def create(self, vals):
        vals["name"] = self._get_seq_with_company("dotacion_code") #self.env["ir.sequence"].next_by_code("dotacion_code")
        #vals["numero"] = self.env["ir.sequence"].next_by_code("dotacion_code")
        print(vals)
        return super().create(vals)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Documento de Dotación debe ser único.')
    ]

