from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    acta_confidencialidad_texto = fields.Html()

    def set_values(self):
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('usuarios.acta_confidencialidad_texto', self.acta_confidencialidad_texto)

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            acta_confidencialidad_texto=params.get_param('usuarios.acta_confidencialidad_texto'),
        )
        return res
