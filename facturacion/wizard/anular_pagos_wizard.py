from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class AccountPayment(models.Model):
    _inherit = "account.payment"

    motivo_anulacion = fields.Text('Motivo anulación pago')

    def action_cancel(self):
        super().action_cancel()

        action = self.env["ir.actions.actions"]._for_xml_id("facturacion.action_motivo_anulacion_pago_wizard")
        ctx = dict()
        if len(self) > 1:
            ctx['active_ids'] = self.ids
        else:
            ctx['default_payment_id'] = self.id

        action.update({
            'context': ctx,
            })
        return action


class MotivoAnulacionPagoWizard(models.TransientModel):
    _name = 'motivo.anulacion.pago.wizard'
    _description = 'Motivo de Anulación Pago Wizard'

    payment_id = fields.Many2one("account.payment")
    motivo = fields.Text('Descripción del Motivo de Rechazo')

    def action_motivo_anulacion(self):
        pagos = self.payment_id
        if not pagos:
            pagos_ids = self.env.context.get('active_ids')
            pagos = self.env['account.payment'].browse(pagos_ids)

        if pagos:
            pagos.sudo().write({
                'motivo_anulacion': self.motivo
            })
            msg = "Anulación de pago por %s " % (self.motivo)
            for pago in pagos:
                pago.message_post(body=msg)

