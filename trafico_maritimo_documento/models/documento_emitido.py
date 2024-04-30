from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class DocumentoEmitido(models.Model):
    _inherit = "tramite.documento.emitido"

    nave_id = fields.Many2one(related='tramite_id.nave_id', store=True, tracking=True)
    #reparto_id = fields.Many2one(related='nave_id.reparto_id', string=_("Reparto"), store=True, tracking=True, readonly=True)
    reparto_origen_id = fields.Many2one(
        related='tramite_id.reparto_origen_id',
        string=_('Juridicción'),
        store=True,
        index=True,
        copy=False,
        help='IMO0112',
        tracking=True)
    reparto_final_id = fields.Many2one(
        related='tramite_id.reparto_final_id',
        string=_('Juridicción'),
        index=True,
        copy=False,
        help='IMO0112',
        tracking=True)

    fecha_origen = fields.Datetime(related='tramite_id.fecha_origen', string="Fecha Origen")
    fecha_destino = fields.Datetime(related='tramite_id.fecha_destino', string="Fecha Destino")

    def _check_tramite_documento_emitido(self, vals):
        tramite_id = self.env['tramite'].browse(vals['tramite_id'])
        if not tramite_id.servicio_id.model_id:
            raise ValidationError(_('Debe configurar el modelo para el servicio: %s.') % (tramite_id.servicio_id.name))
        return tramite_id

    def _prepare_file_name(self):
        report_titulo_name = self.servicio_id.name
        if self.tipo_documento_id.id == self.env.ref("base_sigmap.gente_mar").id:
            report_titulo_name = '%s - %s' % (report_titulo_name, self.personal_maritimo_id.name)
        if self.tipo_documento_id.id in [self.env.ref("base_sigmap.nave").id, self.env.ref("base_sigmap.trafico_maritimo").id]:
            report_titulo_name = '%s - %s' % (report_titulo_name, self.nave_id.name)
        return report_titulo_name

    @api.model
    def create(self, vals):
        tramite_id = self._check_tramite_documento_emitido(vals)
        if tramite_id.tipo_documento_id.id == self.env.ref("base_sigmap.trafico_maritimo").id:
            vals["name"] = self.env["ir.sequence"].next_by_code('documento_trafico_maritimo_sequence_code')
            if not vals["name"]:
                raise ValidationError('No existe secuencial de documento para tráfico marítimo')
        return super().create(vals)