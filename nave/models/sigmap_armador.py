from odoo import api, fields, models, _

class Armador(models.Model):
    _inherit = 'sigmap.armador'

    nave_armador_ids = fields.One2many(
        string=_('Ships'),
        comodel_name='nave.nave.armador',
        inverse_name='armador_id',
        context={'active_test': False})
