from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    pm_dotacion_ids = fields.One2many('trafico.maritimo.crews.list', 'personal_maritimo_id', string='Dotación')
    #pm_dotacion_ids = fields.One2many('trafico.maritimo.crews.list', 'personal_maritimo_id', string='Dotación')


class Dotacion(models.Model):
    _inherit = "permar.documento.dotacion"

    pm_dotacion_ids = fields.One2many(related='personal_maritimo_id.pm_dotacion_ids')