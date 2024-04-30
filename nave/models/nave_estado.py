from odoo import api, fields, models, _

class NaveEstado(models.Model):
    _name = 'nave.nave.estado'
    _description = _( 'Origin')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Description'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    codigo_externo = fields.Char(
        string=_('Código Externo'),
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
    ]
