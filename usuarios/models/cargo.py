from odoo import models, fields, _


class Cargo(models.Model):
    _inherit = 'sigmap.cargo'

    user_ids = fields.One2many('res.users', 'departamento_id', string="Usuarios", tracking=True, copy=False)
