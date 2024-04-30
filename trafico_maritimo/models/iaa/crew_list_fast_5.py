from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #OMI CREW LIST
    crew_list_ids = fields.One2many('iaa.crews.list.declaration', 'vessel_voyage_info_id', string=_("Crew's List Declaration FAL 5"))


class IAACrewListDeclaration(models.Model):
    _name = 'iaa.crews.list.declaration'
    _description = "IAA IMO Crew List Declaration FAL 5"

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    personal_maritimo_id = fields.Many2one('personal.maritimo', string=_('Sea Person'), tracking=True)
    jerarquia_id = fields.Many2one(related='personal_maritimo_id.jerarquia_id', string=_('Rank'), store=True, tracking=True)
    #jerarquia_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string=_("Rank  or rating"))
    nationality = fields.Char(related='personal_maritimo_id.nationality', string=_('Nationality'), readonly=True, tracking=True)
    birthday = fields.Date(related='personal_maritimo_id.birthday', string=_('Date of Birth'), tracking=True)
    numero_libretin = fields.Char(string=_('Seaman Book'))