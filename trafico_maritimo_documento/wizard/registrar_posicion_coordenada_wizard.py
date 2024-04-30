from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class TraficoMaritimoInternacionalCostera(models.Model):
    _inherit = 'trafico.maritimo.internacional.costera'

    def button_genera_coordenada(self):
        self.ensure_one()
        ctx = dict(
            default_trafico_maritimo_internacional_costera_id = self.id,
            default_latitud = self.latitud,
            default_latitud_dms = self.latitud_dms,
            default_longitud = self.longitud,
            default_longitud_dms = self.longitud_dms,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("trafico_maritimo.action_registrar_posicion_coordenada_wizard")
        action.update({
            'context': ctx,
            })
        return action


class RegistrarPosicionCoordenadaWizard(models.TransientModel):
    _inherit = 'registrar.posicion.coordenada.wizard'

    trafico_maritimo_internacional_costera_id = fields.Many2one(
        'trafico.maritimo.internacional.costera',
        string=_('Tráfico Marítimo Internacional Costera'),
        readonly=True,
        tracking=True)

    def action_registrar_posicion_coordenada_nave(self):
        self.ensure_one()
        # self._check_coordenadas()
        #trafico_maritimo_coordenadas = self.trafico_maritimo_internacional_costera_id if self.trafico_maritimo_internacional_costera_id else []
        if self.trafico_maritimo_internacional_costera_id:
            self.trafico_maritimo_internacional_costera_id.sudo().write({
                'latitud': self.latitud,
                'longitud': self.longitud,
                'latitud_dms': self.latitud_dms,
                'longitud_dms': self.longitud_dms,
            })
        return super().action_registrar_posicion_coordenada_nave()