from odoo import models
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class DocumentoBase(models.AbstractModel):
    _inherit = 'tramite.documento.emitido'

    def _get_usuario_sumilla(self):
        sumilla = self.env['sigmap.sumilla'].search([
            ('reparto_id', '=', self.reparto_id),
            ('documento_id', '=', self.documento_id.servicio_id),
        ])

        if not sumilla():
            raise ValidationError(f'No hay sumilla configurada para el documento {self.documento_emitido_id.servicio_id.name} en el reparto {self.reparto_id.name}')

        for responsable_id in sumilla.responsable_ids:
            if not responsable_id.sumilla:
                raise ValidationError(f'El usuario f{responsable_id.user_id} no tiene sumilla configurada')

        return [{'sumilla': ' / '.join(sumilla.responsable_ids.mapped('sumilla'))}]
