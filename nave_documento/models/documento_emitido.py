from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class DocumentoEmitido(models.Model):
    _inherit = "tramite.documento.emitido"

    beneficiario_nave_id = fields.Many2one(
        related='tramite_id.beneficiario_nave_id',
        string=_('Beneficiario'), store=True, tracking=True)
    nave_id = fields.Many2one(related='tramite_id.nave_id', store=True, tracking=True)

    nave_persona = fields.Char(related='tramite_id.nave_persona', store=True)

    nave_inspeccion_id = fields.Many2one(related="tramite_id.nave_inspeccion_id", string=_("Inspección"), tracking=True)
    calificacion_final = fields.Selection(related="tramite_id.nave_inspeccion_id.calificacion_final", string=_('Calificación'), tracking=True)

    @api.model
    def create(self, vals):
        tipo_documento_id = self.env['tramite'].browse(vals['tramite_id']).tipo_documento_id
        if tipo_documento_id.id == self.env.ref("base_sigmap.nave").id:
            vals["name"] = self.env["ir.sequence"].next_by_code("documento_nave_sequence_code")
            if not vals["name"]:
                raise ValidationError('No existe secuencial de documento para nave')
        return super().create(vals)

    def _prepare_file_name(self):
        report_titulo_name = super()._prepare_file_name()
        if self.tipo_documento_id.id == self.env.ref("base_sigmap.nave").id:
            report_titulo_name = '%s - %s' % (self.servicio_id.name, self.nave_id.name)
        return report_titulo_name
