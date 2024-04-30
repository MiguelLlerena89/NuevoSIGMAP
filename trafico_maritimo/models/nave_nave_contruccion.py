from odoo import api, fields, models, _

class NaveConstruccion(models.Model):
    _inherit = 'nave.nave.construccion'

    reparto_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Juridicción'),
        #required=True,
        store=True,
        index=True,
        copy=False,
        tracking=True)

