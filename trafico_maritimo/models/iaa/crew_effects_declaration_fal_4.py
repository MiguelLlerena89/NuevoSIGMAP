from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #OMI CREW´S EFFECTS DECLARATION
    crew_effects_ids = fields.One2many('iaa.crews.effects.declaration', 'vessel_voyage_info_id', string=_("Crew's Effects Declaration"))


class IAACrewEffectsDeclaration(models.Model):
    _name = 'iaa.crews.effects.declaration'
    _description = "IAA IMO Crew's Effects Declaration"

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    personal_maritimo_id = fields.Many2one('personal.maritimo', string=_('Family name / Given names'), store=True, tracking=True)
    #jerarquia_id = fields.Char(related='personal_maritimo_id.jerarquia_id', string=_('Rank'), readonly=True, tracking=True)
    jerarquia_id = fields.Many2one('jerarquia', string=_("Rank  or rating"))
    #rank_id = fields.Many2one('iaa.rank', string=_("Rank  or rating"))
    product_id = fields.Many2one('product.product', string=_('Name of article'), change_default=True)
    qty_received = fields.Float(string=_('Quantity'))
    product_description = fields.Char(string=_('Product Description'))