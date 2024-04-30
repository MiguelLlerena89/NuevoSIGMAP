from odoo import api, fields, models, _

class TipoConstruccion(models.Model):
    _name = 'sigmap.tipo.construccion'
    _description = _('Building Type')
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
