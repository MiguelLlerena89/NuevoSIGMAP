from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _inherit = "iaa.vessel.voyage.information"

    #MEASURES AND PROCEDURES
    measures_ids = fields.One2many(
        'iaa.measures.procedures',
        'vessel_voyage_info_id',
        string=_('Additional Measures'),
        domain=[('measures_procedures_type', '=', 'M')],
    )

    procedures_ids = fields.One2many(
        'iaa.measures.procedures',
        'vessel_voyage_info_id',
        string=_('Security Procedures Ship to Ship'),
        domain=[('measures_procedures_type', '=', 'P')],
    )


class IAAMeasuresProcedures(models.Model):
    _name = 'iaa.measures.procedures'
    _description = 'IAA MEASURES AND PROCEDURES'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    port_id = fields.Many2one('sigmap.puerto', string=_('Port'))
    notes = fields.Text(string=_('Description'))
    measures_procedures_type = fields.Selection([
        ('M', _('Measures')),
        ('P', _('Procedures')),
    ],
    readonly=True, store=True, string=_('Type of Measures and Procedure'), index=True, copy=False, tracking=True)