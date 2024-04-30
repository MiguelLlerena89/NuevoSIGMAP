from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class TramiteDocumentoEmitido(models.Model):
    _inherit = "tramite.documento.emitido"

    def action_invalidar_documento(self):
        self.ensure_one()
        accion = self.env.context.get('default_accion', False)
        if not accion:
            return False
        ctx = dict(self.env.context, default_documento_emitido_id=self.id)
        print(ctx)
        action = self.env["ir.actions.actions"]._for_xml_id("tramite.action_motivo_invalidar_documento_wizard")
        action.update({
            'context': ctx,
            })
        return action


class TramiteDocumentoEmitidoMotivoInvalidarDocumentoWizard(models.TransientModel):
    _name = 'tramite.documento.emitido.motivo.invalidar.documento.wizard'
    _description = 'Motivo de Invalidar Documento Wizard'

    documento_emitido_id = fields.Many2one("tramite.documento.emitido")
    motivo = fields.Text('Motivo')

    def action_motivo_invalidar_documento(self):
        self.ensure_one()
        accion = self.env.context.get('default_accion')
        state = 'suspendido' if accion == 'suspender' else 'anulado'
        if self.documento_emitido_id:
            self.documento_emitido_id.sudo().write({'state': state})
            msg = "El documento ha sido %s por %s " % (state, self.motivo)
            self.documento_emitido_id.message_post(body=msg)
