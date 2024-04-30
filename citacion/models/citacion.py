from odoo import api, fields, models, _
import json

class CitacionContravention(models.Model):
    _name = 'citacion.citacion.contravencion'

    citacion_id = fields.Many2one(
        'citacion.citacion',
        string=_('Citation'))

    articulo_id = fields.Many2one(
        'citacion.contravencion.ley.art',
        string=_('Article'))

    articulo_description = fields.Char(
        string=_('Article'),
        related='articulo_id.description')

    numeral_id_domain = fields.Char(
        string=_('numeral_id domain'),
        compute='_compute_numeral_id_domain',
        store=True,
        precompute=True)

    numeral_id = fields.Many2one(
        'citacion.contravencion.ley.num',
        string=_('Numeral'))

    numeral_description = fields.Char(
        string=_('Numeral'),
        related='numeral_id.description')


    @api.depends('articulo_id')
    def _compute_numeral_id_domain(self):
        for rec in self:
            articulo_id = rec.articulo_id.id if rec.articulo_id else False
            rec.numeral_id_domain = json.dumps([
                ('articulo_id', '=', articulo_id)
            ])
    
    @api.onchange('numeral_id')
    def _onchange_numeral_id(self):
        num = self.numeral_id
        if num and num.articulo_id != self.articulo_id:
            self.articulo_id = num.articulo_id

    @api.onchange('articulo_id')
    def _onchange_articulo_id(self):
        num = self.numeral_id
        if num and num.articulo_id != self.articulo_id:
            self.numeral_id = False


class Citacion(models.Model):
    _name = 'citacion.citacion'
    _description = _( 'Citation')
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sigmap.updated.by']

    READONLY_STATES = { state: [('readonly', True)] for state in {'approved', 'canceled'}}

    document_number = fields.Char(string=_("Citation Nº"))

    reparto_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Distribution'))

    datetime = fields.Datetime(
        string=_('Datetime'))

    datetime_limit = fields.Datetime(
        string=_('Datetime Limit'))

    latitude = fields.Float(
        string=_('Latitude'),
        digits=(10, 7))

    longitude = fields.Float(
        string=_('Longitude'),
        digits=(10, 7))

    latitude_dms = fields.Char(
        compute='_compute_lat_lon_dms',
        precompute=True,
        store=True,
        string=_('Latitude'))

    longitude_dms = fields.Char(
        compute='_compute_lat_lon_dms',
        precompute=True,
        store=True,
        string=_('Longitude'))

    punto_referencia = fields.Char(
        string=_('Reference'))


    nave_tipo_nombre = fields.Char(
        string=_('Ship Type/Name'))

    nave_matricula = fields.Char(
        string=_('Registration Number'))

    nave_trb = fields.Float(
        string=_('TRB'))

    caracteristicas = fields.Char(
        string=_('Ship Characteristics'))

    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Ship'))


    capitan_id = fields.Many2one(
        'personal.maritimo',
        string=_('Captain'))

    capitan_name = fields.Char(
        string=_('Name'))

    capitan_identification_number = fields.Char(
        string=_('Identification number'))


    armador_id = fields.Many2one(
        'sigmap.armador',
        string=_('Charterer'))

    armador_name = fields.Char(
        string=_('Name'))

    armador_identification_number = fields.Char(
        string=_('Identification number'))


    contravencion_ids = fields.One2many(
        comodel_name='citacion.citacion.contravencion',
        inverse_name='citacion_id',
        string=_('Contraventions'))


    more_comments = fields.Char(
        string=_('Other/More information'))


    jefe_id = fields.Many2one(
        'personal.maritimo',
        string=_('Boarding Chief'))

    jefe_grado = fields.Char(
        string=_('Rank'))


    offender_id = fields.Many2one(
        'res.partner',
        string=_('Offender'))

    offender_name = fields.Char(
        string=_('Offender name'))

    offender_identification_number = fields.Char(
        string=_('Offender identification number'))

    state = fields.Selection([
        ('pending', _('Pending')),
        ('warrant', _('Arrest Warrant')),
        ('confirmed', _('Confirmed')),
        ('approved', _('Approved')),
        ('canceled', _('Canceled')),
    ],
    string=_('States'),
    default='pending',
    index=True,
    tracking=True)


    def name_get(self):
        result = []
        for rec in self:
            name = _('Citation Nº')

            if rec.document_number:
                name += ' %s' % (rec.document_number)
            elif rec.id:
                name += ' [%s]' % (rec.id)
            else:
                name += ' [' + _('new') + ']'

            if rec.reparto_id:
                name += ' - %s' % rec.reparto_id.name

            result.append((rec.id, name))

        return result

    @api.onchange('nave_id')
    def _onchange_nave_id(self):
        self.ensure_one()
        if self.nave_id:
            nave = self.nave_id
            self.nave_tipo_nombre = nave.nave_tipo_id.name + " / " + nave.name
            self.nave_matricula = nave.matricula
            self.nave_trb = nave.trb
        else:
            self.nave_tipo_nombre = self.nave_matricula = self.nave_trb = False

    @api.onchange('capitan_id')
    def _onchange_capitan_id(self):
        self.ensure_one()
        if self.capitan_id:
            capitan = self.capitan_id
            self.capitan_name = capitan.name
            self.capitan_identification_number = capitan.vat
        else:
            self.capitan_name = self.capitan_identification_number = False

    @api.onchange('armador_id')
    def _onchange_armador_id(self):
        self.ensure_one()
        if self.armador_id:
            armador = self.armador_id
            self.armador_name = armador.name
            self.armador_identification_number = armador.vat
        else:
            self.armador_name = self.armador_identification_number = False

    @api.onchange('offender_id')
    def _onchange_offender_id(self):
        self.ensure_one()
        if self.offender_id:
            offender = self.offender_id
            self.offender_name = offender.name
            self.offender_identification_number = offender.vat
        else:
            self.offender_name = self.offender_identification_number = False

    @api.depends('latitude', 'longitude')
    def _compute_lat_lon_dms(self):
        def deg_to_dms(deg, pretty_print=None, ndp=4):
            # move to utils.py file

            m, s = divmod(abs(deg)*3600, 60)
            d, m = divmod(m, 60)
            if deg < 0:
                d = -d
            d, m = int(d), int(m)

            if pretty_print:
                if pretty_print=='latitude':
                    hemi = _('N') if d>=0 else _('S')
                elif pretty_print=='longitude':
                    hemi = _('E') if d>=0 else _('W')
                else:
                    hemi = '?'
                return '{d:d}° {m:d}{ms:s} {s:.{ndp:d}f}″ {hemi:1s}'.format(
                            d=abs(d), m=m, ms="'", s=s, hemi=hemi, ndp=ndp)
            return d, m, s

        for rec in self:
            rec.latitude_dms = ""
            rec.longitude_dms = ""
            if rec.latitude:
                lat = rec.latitude
                rec.latitude_dms = deg_to_dms(deg=lat, pretty_print='latitude', ndp=4)
            if rec.longitude:
                lon = rec.longitude
                rec.longitude_dms = deg_to_dms(deg=lon, pretty_print='longitude', ndp=4)

    def action_pending(self):
        self.write({'state': 'pending'})

    def action_warrant(self):
        self.write({'state': 'warrant'})

    def action_confirmed(self):
        self.write({'state': 'confirmed'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_canceled(self):
        self.write({'state': 'canceled'})
