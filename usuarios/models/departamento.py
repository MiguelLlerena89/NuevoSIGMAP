from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class Departamento(models.Model):
    _name = 'sigmap.departamento'
    _inherit = ['sigmap.departamento', 'mail.thread', 'mail.activity.mixin']

    user_ids = fields.One2many('res.users', 'departamento_id', string="Usuarios", tracking=True, copy=False)
