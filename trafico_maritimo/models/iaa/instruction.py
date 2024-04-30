from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAInstruction(models.Model):
    _name = 'iaa.instruction'
    _description = 'IAA Instruction'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string=_('Name'))
    instruction = fields.Text(string=_('Instruction'))
    active = fields.Boolean(string=_('Active'), default=True)

