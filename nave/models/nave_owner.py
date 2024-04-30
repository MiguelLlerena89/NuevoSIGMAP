from odoo import api, fields, models, _

class NaveOwner(models.Model):
    _name = 'nave.nave.owner'
    _description = _('Ship Owner')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    nave_id = fields.Many2one(
        'nave.nave',
        ondelete='restrict',
        required=True,
        copy=False,
        string=_('Ship'))

    fecha_inicio = fields.Date(
        string=_('Start Date'),
        required=True,
        copy=False,
        tracking=True)

    fecha_fin = fields.Date(
        string=_('End Date'),
        required=False,
        copy=False,
        tracking=True)

    # estado [ A | I ]
    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)
