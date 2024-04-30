from odoo import fields, models, _

import logging

_logger = logging.getLogger(__name__)


class Especialidad(models.Model):
    _name = 'sigmap.especialidad'
    _description = 'Especialidad'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    abreviatura = fields.Char(required=True)
    active = fields.Boolean(_('Active?'), default=True)
