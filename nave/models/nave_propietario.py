from odoo import api, fields, models, _

class NavePropietario(models.Model):
    _name = 'nave.nave.propietario'
    _description = _('Relation between the ship and the Ship Owner')
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

    propietario_id = fields.Many2one(
        'sigmap.propietario',
        ondelete='restrict',
        copy=False,
        string=_('Ship Owner'))
    
    tipo_fletamento_int_id = fields.Many2one(
        'sigmap.tipo.fletamento',
        ondelete='restrict',
        copy=False,
        string=_('Charter Type'),
        help=_('Charter Type for foreign ships'))


class Nave(models.Model):
    _inherit = 'nave.nave'

    nave_propietario_ids = fields.One2many(
        string=_('Owners'),
        comodel_name='nave.nave.propietario',
        inverse_name='nave_id')
