from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)


class ResPartnerParentezco(models.Model):
    _name = 'res.partner.parentesco'
    _description = 'Parentesco contacto'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(_('Description'), required=1)
    active = fields.Boolean(_('Active?'), default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique'))
    ]