from odoo import api, fields, models, _

class Armador(models.Model):
    _name = 'sigmap.armador'
    _description = _('Ship Sharterer')
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
        help=_('Information of the partner related to the Ship Sharterer'))

    partner_is_valid = fields.Boolean(
        string=_('Partner is valid?'),
        default=False)

    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)

    image_url = fields.Char(
        related='country_id.image_url',
        readonly=True
    )

    matricula_armador_ids = fields.One2many(
        string=_('Registration numbers'),
        comodel_name='sigmap.matricula.armador',
        inverse_name='armador_id')

    matricula = fields.Char(
        compute='_compute_matricula',
        string=_('Registration Number Code'))
    
    matricula_caducidad = fields.Char(
        compute='_compute_matricula',
        string=_('Registration Number Expiry'))

    matricula_active = fields.Char(
        compute='_compute_matricula',
        string=_('Registration Number Status'))

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        computed_value = False
        if self.partner_id:
            partner_vat = self.partner_id.vat
            charterers_for_partner = self.env['sigmap.armador'].search([('partner_id.vat', '=', partner_vat)])
            if len(charterers_for_partner) == 0:
                computed_value = True
            if len(charterers_for_partner) == 1:
                charterer_id = charterers_for_partner[0].id
                if type(self.id) == int:
                    computed_value =  self.id == charterer_id
                else:
                    computed_value = self.id.origin == charterer_id

        self.partner_is_valid = computed_value

    @api.depends('matricula_armador_ids')
    def _compute_matricula(self):
        for rec in self:
            rec.matricula = ''
            rec.matricula_caducidad = ''
            rec.matricula_active = ''

            if rec.matricula_armador_ids:
                current_matricula = [ reg_num for reg_num in rec.matricula_armador_ids if reg_num['active']]
                if len(current_matricula) == 1:
                    rec.matricula = current_matricula[0]['codigo_documento']
                    rec.matricula_caducidad = current_matricula[0]['fecha_caducidad']
                    rec.matricula_active = _('Active') if current_matricula[0]['active'] else _('Expired')
                if len(current_matricula) < len(rec.matricula_armador_ids):
                    rec.matricula_active = _('Expired')
