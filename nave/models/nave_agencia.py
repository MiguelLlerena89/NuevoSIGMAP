from odoo import api, fields, models, _

class NaveAgencia(models.Model):
    _name = 'nave.nave.agencia.naviera'
    _description = _('Relation between the ship and the Shipping Agency')
    _inherits = {'nave.nave.owner': 'nave_owner_id'}
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    nave_owner_id = fields.Many2one(
        'nave.nave.owner',
        ondelete='restrict',
        auto_join=True,
        copy=False,
        string=_('Related Owner Registry'))
    # overridden inherited fields to bypass access rights, in case you have
    # access to the user but not its corresponding partner

    agencia_id = fields.Many2one(
        'sigmap.agencia.naviera',
        ondelete='restrict',
        copy=False,
        string=_('Shipping Agency'))


class Nave(models.Model):
    _inherit = 'nave.nave'

    nave_agencia_ids = fields.One2many(
        string=_('Shipping Agencies'),
        comodel_name='nave.nave.agencia.naviera',
        inverse_name='nave_id')
