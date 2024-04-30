# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError, UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    dias_disponibles_permiso_provisional = fields.Integer(string="Cantidad de días disponibles para permiso provisional de jerarquía", default=3)
    dias_disponibles_dispensa = fields.Integer(string="Cantidad de días disponibles para dispensas de jerarquía", default=3)

    dirsan_url = fields.Char(string="URL DIRSAN")

    imagen_fondo_matricula = fields.Binary(string='Imagen de Fondo de Matrícula', attachment=True)

    #=== CRUD METHODS ===#

    def set_values(self):
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('personal_maritimo.dias_disponibles_permiso_provisional', self.dias_disponibles_permiso_provisional)
        params.set_param('personal_maritimo.dias_disponibles_dispensa', self.dias_disponibles_dispensa)
        params.set_param('personal_maritimo.dirsan_url', self.dirsan_url)
        params.set_param('personal_maritimo.imagen_fondo_matricula', self.imagen_fondo_matricula)

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            dias_disponibles_permiso_provisional=params.get_param('personal_maritimo.dias_disponibles_permiso_provisional'),
            dias_disponibles_dispensa=params.get_param('personal_maritimo.dias_disponibles_dispensa'),
            dirsan_url=params.get_param('personal_maritimo.dirsan_url'),
            imagen_fondo_matricula=params.get_param('personal_maritimo.imagen_fondo_matricula')
        )
        return res

