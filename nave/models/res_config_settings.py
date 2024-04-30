from ast import literal_eval
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reparto_requiere_ais_ids = fields.Many2many(
        'sigmap.reparto',
        string=_('Repartos que requieren AIS'),
        help=_('Repartos en donde se requiere verificar que las naves tengan un dispositivo AIS registrado'))

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('nave.reparto_requiere_ais_ids', self.reparto_requiere_ais_ids.ids)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        repartos_ids = params.get_param('nave.reparto_requiere_ais_ids')
        records = [(6, 0, literal_eval(repartos_ids))] if repartos_ids and literal_eval(repartos_ids) else False
        res.update(
            reparto_requiere_ais_ids=records,
        )
        return res
