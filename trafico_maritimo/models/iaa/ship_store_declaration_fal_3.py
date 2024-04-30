from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #OMI SHIP´S STORES DECLARATION
    persons_number_onboard = fields.Integer(string=_('Number of persons onboard'))
    period_of_stay = fields.Integer(string=_('Period of stay'))
    place_of_storage = fields.Char(string=_('Place of storage'))
    articles_ids = fields.One2many('iaa.ship.store.declaration', 'vessel_voyage_info_id', string=_("Ship's Store Declaration"))


class IAAShipStoreDeclaration(models.Model):
    _name = 'iaa.ship.store.declaration'
    _description = "IAA IMO Ship's Store Declaration"

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    product_id = fields.Many2one('product.product', string=_('Name of article'), change_default=True)
    qty_received = fields.Float(string=_('Quantity'))
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    office_user_id = fields.Many2one('res.users', string=_('Office User'))
