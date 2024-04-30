from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ActaConfidencialidad(models.Model):
    _name = "acta.confidencialidad"
    _inherit = ["acta.confidencialidad", "tramite.documento.firma"]

    def _prepare_report_data(self):
        return self.env.ref("usuarios.action_acta_confidencialidad_print")

    def _prepare_file_name(self):
        return f'SIGMAP - Acta de confidencialidad - {self.user_id.name}'
