from odoo import api, fields, models, _

class NaveArmador(models.Model):
    _name = 'nave.nave.armador'
    _description = _('Relation between the ship and the Ship Charterer')
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

    armador_id = fields.Many2one(
        'sigmap.armador',
        ondelete='restrict',
        copy=False,
        string=_('Ship Charterer'))


class Nave(models.Model):
    _inherit = 'nave.nave'

    nave_armador_ids = fields.One2many(
        string=_('Charters'),
        comodel_name='nave.nave.armador',
        inverse_name='nave_id')
