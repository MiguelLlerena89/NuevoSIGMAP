import base64
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta


class NaveDocumentoMatricula(models.Model):
    _name = 'nave.documento.matricula'
    _description = 'Matricula de Nave'
    _inherit = "nave.documento.base"

    matricula = fields.Char(
        string=_('Matrícula'),
        related='nave_id.matricula',
        store=True,
        index=True,
        copy=False,
        tracking=True)

    pendiente_generar_matricula = fields.Boolean(string='Pendiente de generar matricula', default=True, store=True, readonly=True)

    def validar(self):
        msg = ''
        if self.pendiente_generar_matricula:
            msg = msg + 'Debe generar la matrícula de la nave %s%s' % (self.nave_id.name,'.\n')
        if msg:
            raise ValidationError(_(msg))
        return True

    @api.model
    def create(self, vals):
        siglas = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id']).nave_id.reparto_id.siglas
        if len(siglas) == 0:
            raise ValidationError('Debe definir el reparto en la nave')
        vals["name"] = self._get_seq_with_reparto(siglas,"documento_matricula_nave_code") #self.env["ir.sequence"].next_by_code("documento_matricula_nave_code")
        return super().create(vals)

    _sql_constraints = [
        ('documento_matricula_nave_id_uniq', 'unique (documento_emitido_id)', 'La matricula de la nave debe ser única.')
    ]
