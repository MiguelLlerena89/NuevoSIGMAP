from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class NaveMatricula(models.Model):
    _name = 'nave.nave.matricula.bitacora'
    _description = _( 'Ship Registration Log')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_names_search = ['name', 'matricula', 'nave_id.name']

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Usuario', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)

    # name = fields.Char(
    #     string=_('Registration'),
    #     #required=True,
    #     index=True,
    #     copy=False,
    #     tracking=True)
    name = fields.Char(
        compute='_compute_name',
        compute_sudo=True,
        store=True,
        index=True,
        copy=False,
        tracking=True)

    tramite_id = fields.Many2one(
        comodel_name='tramite',
        string=_('Tramite'),
        #required=True,
        index=True,
        copy=False,        
        tracking=True)

    fecha_tramite = fields.Date(
        string='Fecha Trámite',
        #required=True,
        index=True,
        copy=False,
        tracking=True)

    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Ship'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    tipo_tramite = fields.Char(
        string=_('Tipo de Trámite'),
        #required=True,
        index=True,
        copy=False,
        tracking=True)
    
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order Reference',
        readonly=True,
        ondelete="cascade",
        index=True,
        copy=False,
        store=True,
        tracking=True)

    matricula = fields.Char(
        string=_('Registration'),
        store=True,
        index=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)

    @api.depends('matricula', 'nave_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = '[%s] %s' % (rec.matricula, rec.nave_id.name) if rec.matricula and rec.nave_id else ""

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name))
        return result

    # @api.depends('name', 'matricula', 'nave_id')
    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         name = '' #rec.name
    #         if rec.matricula:
    #             name += ' [' + rec.matricula + ']'
    #         if rec.nave_id:
    #             name += ' ' + rec.nave_id.name if len(name) > 0 else rec.nave_id.name
    #         result.append((rec.id, name))
    #     return result
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique')),
        ('matricula_uniq', 'unique (matricula)',
            _('The registration must be unique'))
    ]