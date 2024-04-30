from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TipoTrafico(models.Model):
    _name = 'tipo.trafico'
    _description = 'Tipo Tráfico'
    #_order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(_('Description'), required=True, index=True, copy=False, tracking=True)
    
    codigo = fields.Char(
        string=_('Code'),
        required=False,
        index=True,
        copy=False,
        tracking=True)
    
    tipo = fields.Selection([
        ('INT', _('INTERNATIONAL')),
        ('NAC', _('NATIONAL')),
    ], string='Type', required=True, index=True, copy=False, tracking=True)
    active = fields.Boolean(_('Active?'), default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique'))
    ]