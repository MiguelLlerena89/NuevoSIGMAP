from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #OMI GENERAL DECLARATION
    onwer = fields.Selection([('arrival', _('Arrival')),('departure', _('Departure'))], string=_('Onwer'))
    # arrival = fields.Boolean(string=_('Arrival'))
    # departure = fields.Boolean(string=_('Departure'))

    next_port_id = fields.Many2one('sigmap.puerto', string=_('Last port call / Next port of call'))
    certificate_of_registry = fields.Char(string=_('Certificate of registry ( Port date number)'))
    position_of_ship = fields.Char(string=_('Position of the ship in the port (berth or terminal)'))
    voyage_previous = fields.Char(string=_('Brief particulars of voyage (previous/subsequent ports of call; underline where remaining cargo will be discharge'))
    crew_number = fields.Integer(string=_('Number of crew (incl. master)'))
    passanger_number = fields.Integer(string=_('Number of passangers'))
    notes = fields.Html(string=_('Remarks'))
    attached_documents_ids = fields.Many2many("ir.attachment", string=_('Attached documents')) #Attached documents
    cargo_declaration = fields.Boolean(string=_('Cargo Declaration?'))
    ship_stores_declaration = fields.Boolean(string=_("Ship's Stores Declaration?"))
    crew_list = fields.Boolean(string=_('Crew list?'))
    passenger_list = fields.Boolean(string=_('Passenger List?'))
    term_residue_reception = fields.Html(string=_("The ship's requirements in term of waste and residue reception facilities"))
    crew_effects_declaration = fields.Boolean(string=_('Crew Effects Declarations?'))
    maritime_declaration_of_health = fields.Boolean(string=_('Maritime Declaration of Health?'))