from odoo import api, fields, models, _

class MatriculaArmador(models.Model):
    _name = 'sigmap.matricula.armador'
    _description = _('Relation between the registration number and the Ship Charterer')
    _inherits = {'sigmap.owner.matricula': 'owner_matricula_id'}
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    owner_matricula_id = fields.Many2one(
        'sigmap.owner.matricula',
        ondelete='restrict',
        auto_join=True,
        copy=False,
        string=_('Related Registration Number Registry'))
    # overridden inherited fields to bypass access rights, in case you have
    # access to the user but not its corresponding partner

    armador_id = fields.Many2one(
        'sigmap.armador',
        ondelete='restrict',
        copy=False,
        string=_('Ship Charterer'),
        help=_('Ship Charterer to whom the registration number belongs'))
