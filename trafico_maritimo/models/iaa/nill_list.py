from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #OMI NILL LIST
    arms_ammunition = fields.Boolean(string=_('Arms and Ammunition'))
    narcotics = fields.Boolean(string=_('Narcotics'))
    parcel = fields.Boolean(string=_('Parcel'))
    mail = fields.Boolean(string=_('Mail'))
    passenger = fields.Boolean(string=_('Passenger'))
    stowaway = fields.Boolean(string=_('STOWAWAY'))
    thru_cargo = fields.Boolean(string=_('Thru Cargo'))
    birds_or_animals = fields.Boolean(string=_('Birds or Animals'))

# class IAAVesselVoyageInformation(models.Model):
#     _inherit = "iaa.vessel.voyage.information"

#     #OMI NILL LIST
#     nill_list_ids = fields.One2many('iaa.nill.list', 'vessel_voyage_info_id', string=_("Nill List"))


# class IAANillList(models.Model):
#     _name = 'iaa.nill.list'
#     _description = "IAA IMO Nill List"

#     vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
#     arms_ammunition = fields.Boolean(string=_('Arms and Ammunition'))
#     narcotics = fields.Boolean(string=_('Narcotics'))
#     parcel = fields.Boolean(string=_('Parcel'))
#     mail = fields.Boolean(string=_('Mail'))
#     passenger = fields.Boolean(string=_('Passenger'))
#     stowaway = fields.Boolean(string=_('STOWAWAY'))
#     thru_cargo = fields.Boolean(string=_('Thru Cargo'))
#     birds_or_animals = fields.Boolean(string=_('Birds or Animals'))
