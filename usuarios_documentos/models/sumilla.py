from odoo import fields, models, _

import logging

_logger = logging.getLogger(__name__)


class Sumilla(models.Model):
    _inherit = 'sigmap.sumilla'

    documento_id = fields.Many2one('tramite.documento', required=True)
