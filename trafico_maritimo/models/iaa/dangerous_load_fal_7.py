from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #DANGEROUS GOODS MANIFEST
    dangerous_load_ids = fields.One2many('iaa.dangerous.load.declaration', 'vessel_voyage_info_id', string=_("Dangerous Load Declaration FAL 7"))


class IAAPCDangerousLoadDeclaration(models.Model):
    _name = 'iaa.dangerous.load.declaration'
    _description = "IAA IMO Dangerous Goods Manifest FAL 7"

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_('Vessel Voyage Information'), required=True, ondelete='cascade', index=True, copy=False)
    bookin_no = fields.Char(string=_('Booking / Reference Number'), tracking=True)
    container_no = fields.Char(string=_('Mark & Numbers Container ID No.(s) Vehicle Reg.(s)'), tracking=True)
    #package_type_id = fields.Many2one('iaa.package.type', string=_('Numbers and Kind Packages'), tracking=True)
    package_type = fields.Char(string=_('Numbers and Kind Packages'), tracking=True)
    proper_shipping_name = fields.Char(string=_('Proper Shipping Name'), tracking=True)
    class_value = fields.Float(string=_('Class'), tracking=True)
    onu_no = fields.Char(string=_('ONU No.'), tracking=True)
    packing_group = fields.Char(string=_('Packing Group'), tracking=True)
    subsidiary_risk = fields.Char(string=_('Subsidiary Risk (s)'), tracking=True)
    flashpoint = fields.Integer(string=_('Flashpoint (in C.c.c)'), tracking=True)
    marine_pollutant = fields.Char(string=_('Marine Pollutant'), tracking=True)
    mass_gross_net = fields.Float(string=_('Mass (Kg) Gross/Net'), tracking=True)
    ems = fields.Char(string=_('EmS'), tracking=True)