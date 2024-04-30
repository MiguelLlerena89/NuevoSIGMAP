from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TipoLicencia(models.Model):
    _name = 'tipo.licencia'
    _description = 'Tipo de Licencia'
    #_order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(_('Description'))
    active = fields.Boolean(_('Active?'), default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique'))
    ]