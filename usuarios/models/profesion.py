from odoo import models, fields, _


class Profesion(models.Model):
    _name = 'sigmap.profesion'
    _description = 'Profesión'

    name = fields.Char(required=True)
    abreviatura = fields.Char('Abreviatura', required=True)
    active = fields.Boolean(_('Active?'), default=True)
    user_ids = fields.One2many('res.users', 'profesion_id', string="Usuarios", tracking=True, copy=False)
