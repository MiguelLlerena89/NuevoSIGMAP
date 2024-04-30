from odoo import api, fields, models, _

class RepartoTipo(models.Model):
    _name = 'sigmap.reparto.tipo'
    _description = _('Distribution Type')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Name'),
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
            _('The name must be unique'))
    ]
