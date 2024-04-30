from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #MARITIME DECLARATION OF HEATH
    maritime_declaration_heath_ids = fields.One2many('iaa.maritime.declaration.heath', 'vessel_voyage_info_id', string=_("Maritime Declaration Heath"))


class IAAMaritimeDeclarationHeath(models.Model):
    _name = 'iaa.maritime.declaration.heath'
    _description = 'IAA Marine Declaration Heath'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    personal_maritimo_id = fields.Many2one('personal.maritimo', string=_('Class or Rating'), store=True, tracking=True)
    age = fields.Integer(related='personal_maritimo_id.age', string=_('Age'), tracking=True)
    genero = fields.Selection(related='personal_maritimo_id.genero', string=_('Sex'), tracking=True)
    nationality = fields.Char(related='personal_maritimo_id.nationality', string=_('Nationality'), readonly=True, tracking=True)
    port_id = fields.Many2one('sigmap.puerto', string=_('Port Joined Ship/Vessel'))
    date = fields.Date(string=_('Date Joined Ship/Vessel'))
    nature_illness = fields.Char(string=_('Nature of Illness'))
    date_onset_symptoms = fields.Date(string=_('DATE OF ONSET OF SYMPTOMS'), tracking=True)
    reported_to_a_port_medical_officer = fields.Boolean(string=_('Reported to a Port Medical Officer?'))
    disposal_of_case = fields.Char(string=_('Disposal of Case'))
    medicines_treatment = fields.Char(string=_('Drugs, Medicines or other treatment given to patient'))
    notes = fields.Text(string=_('Comments'))