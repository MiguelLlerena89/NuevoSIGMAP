from odoo import fields, models, _

import logging

_logger = logging.getLogger(__name__)


class Departamento(models.Model):
    _name = 'sigmap.departamento'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Departamento'

    name = fields.Char(required=True)
    active = fields.Boolean(_('Active?'), default=True)
