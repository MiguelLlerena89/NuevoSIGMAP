from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Jurisdiccion(models.Model):
    _name = 'sigmap.jurisdiccion'
    _description = 'Jurisdicción'

    name = fields.Char(string=_('Nombre'))
    active = fields.Boolean(_('active'))
