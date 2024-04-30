from odoo import api, fields, models, _

class PuertoRegistro(models.Model):
    _name = 'sigmap.puerto.registro'
    _description = _('Port')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Name'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    codigo = fields.Char(
        string=_('Code'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    country_id = fields.Many2one(
        'res.country',
        ondelete='restrict',
        string=_('Country'),
        required=False,
        copy=False,
        tracking=True)

    country_code = fields.Char(
        related='country_id.code',
        string=_('Country Code'))

    latitude = fields.Float(
        string=_('Latitude'),
        digits=(10, 7))

    longitude = fields.Float(
        string=_('Longitude'),
        digits=(10, 7))

    domain = fields.Char(
        string=_('Website Domain'),
        copy=False,
        help=_('E.g. https://www.mydomain.com'),
        tracking=True)

    tipo = fields.Selection([
            ('pub', _('Public')),
            ('pri', _('Private')),
            ('esp', _('Special Port')),
        ],
        string=_('Type'),
        #required=True,
        index=True,
        copy=False,
        tracking=True)

    tipo_trafico = fields.Selection([
            ('int', _('International')),
            ('nac', _('National')),
        ],
        string=_('Traffic Type'),
        #required=True,
        index=True,
        copy=False,
        tracking=True)

    reparto_id = fields.Many2one(
        'sigmap.reparto',
        ondelete='restrict',
        string=_('Related Distribution'),
        #required=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique')),
        ('code_uniq', 'unique (codigo)',
            _('The code must be unique'))
    ]
