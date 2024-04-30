from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class TraficoMaritimoNavegacion(models.Model):
    _inherit = 'trafico.maritimo.navegacion'

    #CARGO DECLARATION
    cargo_ids = fields.One2many('trafico.maritimo.cargo', 'trafico_maritimo_navegacion_id', string=_("Cargo Declaration FAL 2"))


class TraficoMaritimoCargo(models.Model):
    _name = 'trafico.maritimo.cargo'

    trafico_maritimo_navegacion_id = fields.Many2one('trafico.maritimo.navegacion', string=_("Tráfico Marítimo Navegación"), ondelete='cascade', index=True, copy=False)
    bookin_no = fields.Char(string=_('Booking / Reference Number'), tracking=True)
    container_no = fields.Char(string=_('Marks and Numbers'), tracking=True)
    #package_type_id = fields.Many2one('iaa.package.type', string=_('Number and kind of packages; description of goods or, if available, the HS Code'), tracking=True)
    package_type = fields.Char(string=_('Number and kind of packages; description of goods or, if available, the HS Code'), tracking=True)
    gross_weight = fields.Float(string=_('Gross weight'), tracking=True)
    measurement = fields.Float(string=_('Measurement'), tracking=True)