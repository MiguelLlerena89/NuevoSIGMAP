from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class TramiteRequisitoCurso(models.Model):
    _inherit = "tramite.requisito.curso"

    documento_emitido_id = fields.Many2one(
        "tramite.documento.emitido",
        string=_("Documento emitido"),
        compute="_compute_documento_emitido"
    )

    @api.depends('personal_maritimo_curso_id')
    def _compute_documento_emitido(self):
        for requisito in self:
            # check tiempo máximo de validez de documentos
            params = self.env['ir.config_parameter'].sudo()
            tiempo_minimo_validez_documentos=params.get_param("tramite.tiempo_minimo_validez_documentos")
            fecha_tope = date.today() + relativedelta(months=int(tiempo_minimo_validez_documentos))
            if requisito.tramite_id.servicio_id.check_refrendo:
                data = [
                    ("personal_maritimo_id", "=", requisito.tramite_id.personal_maritimo_id.id),
                    ("curso_persona_id", "=", requisito.personal_maritimo_curso_id.id),
                    ("fecha_caducidad", ">=", fecha_tope)
                ]
                if requisito.curso_id.tipo_curso_id:
                    model = requisito.curso_id.tipo_curso_id.model_model
                    doc = self.env[model].search(data, limit=1)
                    if doc:
                        requisito.documento_emitido_id = doc.documento_emitido_id.id
                        requisito.completado = True
                    else:
                        requisito.completado = False
                        requisito.documento_emitido_id = False
                else:
                        requisito.completado = False
                        requisito.documento_emitido_id = False
            else:
                requisito.documento_emitido_id = False

    def _inverse_documento_emitido_edit(self):
        pass
