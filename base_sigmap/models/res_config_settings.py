from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    #_description = 'Parámetros Ws DINARP'

    url = 'https://interoperabilidad.dinardap.gob.ec/interoperador-v2?wsdl'
    dinarp_url = fields.Char(string="URL DINARP", default=url)

    #=== CRUD METHODS ===#

    def set_values(self):
        if self.sri_clave_acceso_size < 0:
            raise UserError(_("Clave de acceso debe ser mayor a 0."))
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('base_sigmap.dinarp_url', self.dinarp_url)

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            dinarp_url=params.get_param('base_sigmap.dinarp_url')
        )
        return res


