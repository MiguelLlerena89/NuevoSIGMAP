from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class IAAVesselVoyageInformation(models.Model):
    _name = "iaa.vessel.voyage.information"
    _description = "IAA Veseel Voyage Information"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_names_search = ['name', 'nave_id']
    _order = 'id desc'

    name = fields.Char(string='Nombre', readonly=True, store=True, index=True, copy=False, tracking=True)

    #1. GENERAL INFORMATION OF VESSEL
    nave_id = fields.Many2one('nave.nave', string=_('Vessel'), domain = "[('tipo', '=', 'INT')]", required=True, index=True, copy=True, tracking=True)
    call_sign = fields.Char(string=_("Call Sign"),
        related='nave_id.senial_llamada',
        readonly=True,
        store=True,
        index=True,
        help="IMO0136",
        tracking=True)

    bandera_pais_id = fields.Many2one(string=_("Ship Register (Flag)"),
        related='nave_id.bandera_pais_id',
        required=True,
        index=True,
        help="IMO0138",
        tracking=True)

    omi_number = fields.Char(string=_("IMO Number"),
        related='nave_id.omi_number',
        readonly=True,
        store=True,
        index=True,
        help="IMO0140",
        tracking=True)

    # ship_type = fields.Selection([
    #     ('miltipurpose', 'MILTIPURPOSE'),
    # ], string=_('Type of Ship'), default='MILTIPURPOSE', index=True, copy=False, tracking=True)
    nave_tipo_id = fields.Many2one('nave.nave.tipo',
        string=_('Type of Ship'),
        related='nave_id.nave_tipo_id',
        readonly=True,
        store=True,
        index=True,
        help='IMO0160',
        tracking=True)
    build_year = fields.Date(string=_('Year of Build'), required=True, index=True) #, default=fields.Date.today
    port_id = fields.Many2one('sigmap.puerto',
        string=_('Port of Registry'),
        index=True,
        copy=False,
        help='IMO0112',
        tracking=True)
    date_registry = fields.Date(string=_('Date of Registry'), required=True, index=True) #, default=fields.Date.today

    loa = fields.Float(_('Lenght overall (LOA)'), required=True)
    lpp = fields.Float(_('Lenght b. Per (LPP)'), required=True)
    lenght = fields.Float(_('Lenght (*)'), required=True)
    trb = fields.Float(related='nave_id.trb', string=_('Gross Tonnage'))
    trn = fields.Float(related='nave_id.trb', string=_('Net Tonnage'))
    deadweit = fields.Float(_('Deadweit'), required=True)

    shipping_line_id = fields.Many2one('res.partner', string=_('Shipping Line'))
    breadth = fields.Float(_('Breadth'), required=True)
    depth = fields.Float(_('Depth'), required=True)
    arrival_draught = fields.Float(_('Arrival Draught'), required=True)
    design_draught = fields.Float(_('Design Draught'), required=True)

    shipping_line_id = fields.Many2one('res.partner', string=_('Shipping Line')) #Shipping Li
    shipowner_id = fields.Many2one('res.partner', string=_('Shipowner'))
    mmsi = fields.Char(string='MMSI',
        related='nave_id.mmsi',
        readonly=True,
        store=True,
        index=True,
        copy=False,
        tracking=True
    )
    classification_society = fields.Char(string=_('Classification Society'))
    security_level_type = fields.Selection([
        ('1', '1'),
    ], string=_('Security Level'), index=True, copy=False, tracking=True)

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('ingresado', 'Ingresado'),
        ('revision', 'Revisión'),
        ('aceptado', 'Aceptado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado', default='borrador', index=True, copy=False, tracking=True)

    company_id = fields.Many2one('res.company', string=_('Company'), required=True, index=True, default=lambda self: self.env.company.id)
    user_id = fields.Many2one(
        'res.users', string=_('User'), index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    active = fields.Boolean(default=True)

    #2. INTERNATIONAL SHIP SECURITY CERTIFICATE
    date_issuance = fields.Date(string=_('Date of Issuance'), required=True, index=True, copy=False, default=fields.Date.today)
    # certificate_type = fields.Selection([
    #     ('approved', _('Approved')),
    #     ('interim', _('Interim')),
    #     ('final', 'Final'),
    # ], string=_('Type of Certificate'), index=True, copy=False, tracking=True)
    approved_certificate_type = fields.Boolean(default=False, index=True, copy=False, tracking=True)
    interim_certificate_type = fields.Boolean(default=False, index=True, copy=False, tracking=True)
    final_certificate_type = fields.Boolean(default=False, index=True, copy=False, tracking=True)

    vessel_security_plan = fields.Boolean(string=_('Vessel Security Plan implemented?'), index=True, copy=False, tracking=True)

    # indicate_certificate_interim  = fields.Selection([
    #     ('change_owner', _('Change of Owner / Operat')),
    #     ('new_to', _('New to / re-entry into sea')),
    #     ('transfer_vessel', _('Transfer of vesseles')),
    # ], string=_('Indicate reason if the certificate is Interim'), index=True, copy=False, tracking=True)
    change_owner_certificate_interim = fields.Boolean(default=False, index=True, copy=False, tracking=True)
    new_to_certificate_interim = fields.Boolean(default=False, index=True, copy=False, tracking=True)
    transfer_vessel_certificate_interim = fields.Boolean(default=False, index=True, copy=False, tracking=True)
    flag_administration = fields.Char(_('Flag Administration or RSO'))

    #2.1 SECURITY MARITIME OFFICERS
    sso_id = fields.Many2one('res.partner', string=_('SSO Name'))
    sso_name = fields.Char(_('SSO Name'))
    duties_on_board = fields.Char(_('Position or Duties on board'))
    sso_email_address = fields.Char(related='sso_id.email', string=_('Email Address'))

    cso_id = fields.Many2one('res.partner', string=_('CSO Name'))
    cso_name = fields.Char(_('CSO Name'))
    cso_phone_number = fields.Char(related='cso_id.phone', related_sudo=False, readonly=False, string=_('Telephone Number - 24 Hour '))
    cso_email_address = fields.Char(related='cso_id.email', string=_('Email Address'))

    reporting_party_id = fields.Many2one('res.partner', string=_('Reporting Party Name'))
    reporting_party_name = fields.Char(_('Reporting Party Name'))
    reporting_compamy = fields.Char(_('Reporting Company / Shipping Agency'))
    reporting_party_email_address = fields.Char(related='reporting_party_id.email', string=_('Email Address'))

    #3. VOYAGE INFORMATION
    port_id = fields.Many2one('sigmap.puerto',_('Destination Port or Place/City'))
    eta = fields.Datetime(string=_('Estimated Date & Time of Arrival'), required=True, index=True, copy=False, default=fields.Datetime.now)
    etd = fields.Datetime(string=_('Estimated Date & Time of Departure'), required=True, index=True, copy=False, default=fields.Datetime.now)
    terminal = fields.Char(string=_('Destination Receiving Facility/Terminal/Anchorage'))
    caption_port_office = fields.Char(string=_('Captain of Port Office/Superintendencia involved'))
    contact_port = fields.Char(string=_('Point of Contact on Port - 24 hour (Shipping Agency and Agent)'))
    contact_port_phone = fields.Char(string=_('Telephon Number'))
    contact_port_email = fields.Char(string=_('Email Address'))

    #3.1 LAST TEN PORTS
    last_ports_ids = fields.One2many('iaa.vessel.voyage.information.line', 'vessel_voyage_info_id', string=_("Last Ten Port's"))

    #3.2 CARGO
    description_cargo = fields.Char(_('General Description of Cargo'))
    amount_cargo = fields.Float(_('Cargo Amount'))
    dangerous_cargo = fields.Boolean(string=_('Dangerous Cargo on board?'))

    # #OMI GENERAL DECLARATION
    # onwer = fields.Selection([('arrival', _('Arrival')),('departure', _('Departure'))], string=_('Onwer'))
    # certificate_of_registry = fields.Char(string=_('Certificate of registry ( Port date number)'))
    # position_of_ship = fields.Char(string=_('Position of the ship in the port (berth or terminal)'))
    # voyage_previous = fields.Char(string=_('Brief particulars of voyage (previous/subsequent ports of call; underline where remaining cargo will be discharge'))
    # crew_number = fields.Integer(string=_('Number of crew (incl. master)'))
    # passanger_number = fields.Integer(string=_('Number of passangers'))
    # notes = fields.Html(string=_('Remarks'))
    # attached_documents_ids = fields.Many2many("ir.attachment", string=_('Attached documents')) #Attached documents
    # cargo_declaration = fields.Boolean(string=_('Cargo Declaration?'))
    # ship_stores_declaration = fields.Boolean(string=_("Ship's Stores Declaration?"))
    # crew_list = fields.Boolean(string=_('Crew list?'))
    # passenger_list = fields.Boolean(string=_('Passenger List?'))
    # term_residue_reception = fields.Html(string=_("The ship's requirements in term of waste and residue reception facilities"))
    # crew_effects_declaration = fields.Boolean(string=_('Crew Effects Declarations?'))
    # maritime_declaration_of_health = fields.Boolean(string=_('Maritime Declaration of Health?'))

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         name = 'IAA - %s - %s' % (rec.nave_id.name, rec.imo_number)
    #         result.append((rec.id, name))
    #     return

    def action_procesar(self):
        self.write({'state': 'ingresado'})

    def action_revisar(self):
        self.write({'state': 'revision'})

    def action_confirmar(self):
        self.write({'state': 'aceptado'})

    def action_cancelar(self):
        self.write({'state': 'cancelado'})

    def _get_seq_with_iaa(self, nave, code):
        return '%s-%s-%s-%s' % ('IAA', nave.name, 'IMO-' + str(nave.omi_number), self.env["ir.sequence"].next_by_code(code))

    @api.model
    def create(self, vals):
        nave = self.env['nave.nave'].browse(vals.get('nave_id'))
        vals["name"] = self._get_seq_with_iaa(nave,"trafico_maritimo_iaa_code") if not vals.get('name') else vals.get('name')
        return super().create(vals)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        name_new = self._get_seq_with_iaa(self.nave_id,"trafico_maritimo_iaa_code")
        default = dict(default or {}, name=_("%s") % (name_new))
        return super(IAAVesselVoyageInformation, self).copy(default)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_if_state(self):
        if self.state != 'borrador':
            raise UserError(_('No puede eliminar el registro: %s ya que tiene un estado diferente a borrador.') % (self.name))

class LastPorts(models.Model):
    _name = 'iaa.vessel.voyage.information.line'
    _description = "Vessel Voyage Information Line"

    vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
    port_id = fields.Many2one('sigmap.puerto', string=_('Port of Registry'))
    date_arrival = fields.Date(string=_('Date of Arrival'))
    date_departure = fields.Date(string=_('Date of Departure'))
    security_level_type = fields.Selection([('1', '1'),], string=_('Security Level'))
    vessel_security_plan = fields.Boolean(string=_('Vessel Security Plan implemented?'))
    additional_measures = fields.Boolean(string=_('Additional Measures?'))
    procedures_ship_to_ship = fields.Boolean(string=_('Procedures Ship to Ship?'))

# class IAAShipStoreDeclaration(models.Model):
#     _name = 'iaa.ship.store.declaration'
#     _description = "IAA IMO Ship's Store Declaration"

#     vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
#     product_id = fields.Many2one('product.product', string=_('Name of article'), change_default=True)
#     qty_received = fields.Float(string=_('Quantity'))
#     product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
#     office_user_id = fields.Many2one('res.users', string=_('Office User'))


# class IAACrewEffectsDeclaration(models.Model):
#     _name = 'iaa.crews.effects.declaration'
#     _description = "IMO Crew's Effects Declaration"

#     vessel_voyage_info_id = fields.Many2one('iaa.vessel.voyage.information', string=_("Vessel Voyage Information"), required=True, ondelete='cascade', index=True, copy=False)
#     family_name = fields.Char(string=_('Family name / Given names'))
#     rank_id = fields.Many2one('iaa.rank', string=_("Rank  or rating"))
#     product_id = fields.Many2one('product.product', string=_('Name of article'), change_default=True)
#     qty_received = fields.Float(string=_('Quantity'))
#     product_description = fields.Char(string=_('Product Description'))
