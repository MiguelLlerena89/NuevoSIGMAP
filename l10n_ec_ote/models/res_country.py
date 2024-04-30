from odoo import api, models, fields, _


class ResCountry(models.Model):
    _inherit = 'res.country'

    nationality = fields.Char(string=_('Nationality (Country)'), tracking=True)