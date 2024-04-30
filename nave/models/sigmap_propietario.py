from odoo import api, fields, models, _

class Propietario(models.Model):
    _inherit = 'sigmap.propietario'

    nave_propietario_ids = fields.One2many(
        string=_('Ships'),
        comodel_name='nave.nave.propietario',
        inverse_name='propietario_id',
        context={'active_test': False})
