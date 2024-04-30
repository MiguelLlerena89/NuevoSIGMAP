from odoo import api, fields, models, _

# IAA PErsona
class IAAPersona(models.Model):
    _name = 'iaa.persona'
    _description = _('IAA Person')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _#rec_names_search = ['name', 'email', 'vat']  # TODO vat must be sanitized the same way for storing/searching

    @property
    def SELF_READABLE_FIELDS(self):
        """ The list of fields a user can read on their own user record.
        In order to add fields, please override this property on model extensions.
        """
        return [
            'signature', 'company_id', 'login', 'email', 'name', 'image_1920',
            'image_1024', 'image_512', 'image_256', 'image_128', 'lang', 'tz',
            'tz_offset', 'groups_id', 'partner_id', '__last_update', 'action_id',
            'avatar_1920', 'avatar_1024', 'avatar_512', 'avatar_256', 'avatar_128',
            'share',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """ The list of fields a user can write on their own user record.
        In order to add fields, please override this property on model extensions.
        """
        return ['signature', 'action_id', 'company_id', 'email', 'name', 'image_1920', 'lang', 'tz']

    partner_id = fields.Many2one(
        'res.partner',
        ondelete='restrict',
        auto_join=True,
        index=True,
        copy=False,
        tracking=True,
        string=_('Related partner'),
        help=_('Information of the partner related to the Ship Owner'))

    partner_is_valid = fields.Boolean(
        string=_('Partner is valid?'),
        default=False)

    active = fields.Boolean(
        string=_('Active?'),
        default=True,
        tracking=True)

    image_url = fields.Char(
        related='country_id.image_url',
        readonly=True
    )