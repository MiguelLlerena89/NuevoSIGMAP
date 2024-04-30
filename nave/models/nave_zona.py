from odoo import api, fields, models, _

class NaveZona(models.Model):
    _name = 'nave.nave.zona'
    _description = _('Zona Marítima')

    name = fields.Char(
        string=_('Name'),
        required=True)
    
    active = fields.Boolean(
        string=_("Active?"),
        default=True)
