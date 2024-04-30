from odoo import fields, models, _, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_ec_parish_id = fields.Many2one(
        "l10n.ec.parish",
        ondelete="restrict",
        string="Parish",
    )

    city_id = fields.Many2one("res.city", string=_('City'), domain="[('country_id','=',country_id),('state_id','=',state_id)]", ondelete='restrict')

    @api.onchange('city_id','city')
    def onchange_city_id(self):
        if self.city_id:
            self.city = self.city_id.name
            self.country_id = self.city_id.country_id.id
            self.state_id = self.city_id.state_id.id