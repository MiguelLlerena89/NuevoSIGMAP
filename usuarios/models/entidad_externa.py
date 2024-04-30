from odoo import models, fields, _


class EntidadExterna(models.Model):
    _name = 'sigmap.entidad.externa'
    _description = 'Entidad Externa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    active = fields.Boolean(_('Active?'), default=True)

    user_ids = fields.One2many('res.users', 'entidad_externa_id', string="Usuarios", tracking=True, copy=False)
