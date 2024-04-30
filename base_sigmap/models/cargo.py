from odoo import models, fields, _


class Cargo(models.Model):
    _name = 'sigmap.cargo'
    _description = 'Cargo'

    name = fields.Char(required=True)
    active = fields.Boolean(_('Active?'), default=True)
