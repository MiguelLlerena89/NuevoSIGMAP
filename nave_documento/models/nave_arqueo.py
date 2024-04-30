from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

class NaveDocumentoArqueo(models.Model):
    _name = 'nave.documento.arqueo'
    _description = 'Certificado Internacional Arqueo'
    _inherit = "nave.documento.base"

    @api.model
    def create(self, vals):
        vals["name"] = self._get_seq_with_company("documento_arqueo_code") #self.env["ir.sequence"].next_by_code("documento_arqueo_code")
        print(vals)
        return super().create(vals)

    _sql_constraints = [
        ('documento_internacional_arqueo_nave_uniq', 'unique (documento_emitido_id)', 'El certificado internacional de arqueo de la nave debe ser único.')
    ]
