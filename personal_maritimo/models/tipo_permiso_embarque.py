from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class PermisoProvisionalEmbarqueTipo(models.Model):
    _name = 'permar.permiso.provisional.embarque.tipo'
    _description = "Permiso provisional de embarque tipo"

    name = fields.Char(string=_("Nombre"), size=100, index=True, tracking=True)