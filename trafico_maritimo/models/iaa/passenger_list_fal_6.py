from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #PASSENGERS LIST
    passengers_list_ids = fields.One2many('iaa.passenger.list.declaration', 'vessel_voyage_info_id', string=_("Passenger's List Declaration FAL 6"))


class IAAPassengerListDeclaration(models.Model):
    _name = 'iaa.passenger.list.declaration'
    _description = "IAA IMO Passenger List Declaration FAL 6"

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    personal_maritimo_id = fields.Many2one('personal.maritimo', string=_('Full name'), store=True, tracking=True)
    nationality = fields.Char(related='personal_maritimo_id.nationality', string=_('Nationality'), readonly=True, store=True, tracking=True)
    birthday = fields.Date(related='personal_maritimo_id.birthday', string=_('Date of Birth'), readonly=True, store=True, tracking=True)
    l10n_latam_identification_type_id = fields.Many2one(related='personal_maritimo_id.l10n_latam_identification_type_id', string=_('Type of identity document'), readonly=True, store=True, tracking=True)
    vat = fields.Char(related='personal_maritimo_id.vat', string=_('Serial Number ID'), readonly=True, store=True, tracking=True)
    port_embarkation_id = fields.Many2one('sigmap.puerto', string=_('Port of Embarkation'))
    port_disembarkation_id = fields.Many2one('sigmap.puerto', string=_('Port of disembarkation'))
    passeger_trafic = fields.Boolean(string=_('Passenger Traffic'))