from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

import logging

_logger = logging.getLogger(__name__)
class DocumentoEvaluacion(models.Model):
    _name = 'permar.documento.evaluacion'
    _description = 'Documento Evaluación'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Descripción', required=True)
    personal_maritimo_id = fields.Many2one('personal.maritimo', 'Persona', tracking=True)
    numero_oficio = fields.Char('Número oficio')
    antecedente = fields.Text('Antecedente')
    analisis = fields.Text('Análisis')
    conclusion = fields.Text('Conclusión')
    recomendacion = fields.Text('Recomendación')
    fecha_informe = fields.Date(string='Fecha Informe')
    centro_formacion_id = fields.Many2one('centro.formacion', string='Centro Realización', index=True, copy=False, tracking=True)
    active = fields.Boolean(string='Activo?', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Documento de evaluación ya existe!"),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self._get_seq_with_company("documento_evaluacion_code") #self.env["ir.sequence"].next_by_code("documento_evaluacion_code")
        return super().create(vals_list)
