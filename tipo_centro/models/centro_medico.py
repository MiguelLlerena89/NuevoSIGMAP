from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)


class CentroMedico(models.Model):
    _name = 'centro.medico'
    _description = 'Centro Médico'
    #_order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(_('Descripción'), required=1)
    country_id = fields.Many2one('res.country', string='País', tracking=True)
    active = fields.Boolean(_('Active?'), default=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)
