from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta


class NaveDocumentoVareDesvare(models.Model):
    _name = 'nave.documento.vare.desvare'
    _description = 'Documento Vare/Desvare en Nave'
    _inherit = "nave.documento.base"

    varadero_id = fields.Many2one('nave.empresa.mantenimiento', string='Varadero', index=True, copy=False, tracking=True)
    fecha_vare = fields.Date('Fecha de Vare', index=True, copy=False, tracking=True) #default=fields.Datetime.today
    fecha_desvare = fields.Date('Fecha de DesVare', index=True, copy=False, tracking=True) #default=fields.Datetime.today,

    def validar(self):
        msg = ''
        # if not self.beneficiario_nave_id:
        #     msg = msg + 'Debe definir el solicitante.\n'
        if not self.varadero_id:
            msg = msg + 'Debe definir el varadero.\n'
        if not self.fecha_vare:
            msg = msg + 'Debe definir la fecha de vare.\n'
        if not self.fecha_desvare:
            msg = msg + 'Debe definir la fecha de desvare.\n'
        if not self.observacion:
            msg = msg + 'Debe ingresar los trabajos a realizarse en las obvervaciones.\n'
        if msg:
            raise ValidationError(_(msg))
        return True

    @api.model
    def create(self, vals):
        siglas = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id']).nave_id.reparto_id.siglas
        if len(siglas) == 0:
            raise ValidationError('Debe definir el reparto en la nave')
        vals["name"] = self._get_seq_with_reparto(siglas,"documento_vare_desvare_code")
        return super().create(vals)

    _sql_constraints = [
        ('documento_vare_desvare_nave_id_uniq', 'unique (documento_emitido_id)', 'El Certificado de Vare/Desvare de la nave debe ser único.')
    ]
