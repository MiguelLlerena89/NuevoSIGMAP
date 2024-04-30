from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class TraficoMaritimoZarpe(models.Model):
    _inherit = 'trafico.maritimo.zarpe'

    def button_control_combustible_nave_wizard(self):
        self.ensure_one()
        ctx = dict(
            default_trafico_maritimo_zarpe_id = self.id,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("trafico_maritimo_documento.action_control_combustible_nave_wizard")
        action.update({
            'context': ctx,
            })
        return action

class ControlCombustibleNaveWizard(models.TransientModel):
    _name = 'control.combustible.nave.wizard'
    _description = 'Control de Combustible en Nave Wizard'

    trafico_maritimo_zarpe_id = fields.Many2one('trafico.maritimo.zarpe', string=_('Trafico Maritimo Zarpe'), readonly=True)
    numero_documento_control = fields.Char(string=_('Número de documento de control'), required=True)

    distribuidora_id = fields.Selection([
        ('distrilider', 'DIRTRILIDER S.A.'),
        ('petrocomercial', 'PETROCOMERCIAL'),
        ('salinas', 'SALINAS YACHT'),
    ], string=_('Origen'), required=True)

    def action_control_combustible_nave(self):
        self.ensure_one()
        self.trafico_maritimo_zarpe_id.sudo().write({
            #'volumen': 1000.00,
            'guia_remision': self.numero_documento_control
        })
        return True
