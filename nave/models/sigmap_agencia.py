from odoo import api, fields, models, _

class AgenciaNaviera(models.Model):
    _inherit = 'sigmap.agencia.naviera'

    nave_agencia_ids = fields.One2many(
        string=_('Ships'),
        comodel_name='nave.nave.agencia.naviera',
        inverse_name='agencia_id')
