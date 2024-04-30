from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class Tramite(models.Model):
    _inherit = "tramite"

    motivo = fields.Text('Descripción del Motivo de Rechazo')

    def action_rechazar(self):
        self.ensure_one()
        ctx = dict(
            default_tramite_id = self.id,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("tramite.action_tramite_motivo_rechazo_wizard")
        action.update({
            'context': ctx,
            })
        return action


class TramiteMotivoRechazoWizard(models.TransientModel):
    _name = 'tramite.motivo.rechazo.wizard'
    _description = 'Tramite Motivo de Rechazo Wizard'

    tramite_id = fields.Many2one("tramite")
    motivo = fields.Text('Descripción del Motivo de Rechazo')

    def action_motivo_rechazo(self):
        self.ensure_one()
        if self.tramite_id:
            self.tramite_id.sudo().write({
                'state': 'rechazado',
                'motivo': self.motivo
            })
            msg = "El trámite ha sido rechado por %s " % (self.motivo)
            self.tramite_id.message_post(body=msg)
