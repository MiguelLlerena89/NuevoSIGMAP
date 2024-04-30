from odoo import fields, models, _

import logging

_logger = logging.getLogger(__name__)


class Distribuidora(models.Model):
    _name = 'sigmap.distribuidora'
    _description = 'Distribuidora'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    active = fields.Boolean(_('Active?'), default=True)

    user_ids = fields.One2many('res.users', 'distribuidora_id', string="Usuarios", tracking=True, copy=False)
