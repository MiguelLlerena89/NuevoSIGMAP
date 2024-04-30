from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #OMI CREW  VACCINATION LIST
    crew_vaccinated_list_ids = fields.One2many('iaa.crew.vaccinated.list', 'vessel_voyage_info_id', string=_("IMO Crew's Vaccinated List"))


class IAACrewVaccinatedList(models.Model):
    _name = 'iaa.crew.vaccinated.list'
    _description = "IAA OMI CREW  VACCINATION LIST "

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    personal_maritimo_id = fields.Many2one('personal.maritimo', string=_('Family name / Given names'), store=True, tracking=True)
    #jerarquia_id = fields.Char(related='personal_maritimo_id.jerarquia_id', string=_('Rank'), readonly=True, tracking=True)
    jerarquia_id = fields.Many2one('jerarquia', string=_("Rank  or rating"))
    #rank_id = fields.Many2one('iaa.rank', string=_('Rank'))
    date_vaccination = fields.Date(string=_('Date of Vaccinated'), tracking=True)
    date_expire_vaccination = fields.Date(string=_('Date of Expiration vaccinated'), tracking=True)