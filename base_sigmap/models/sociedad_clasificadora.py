from odoo import api, fields, models, _

class SociedadClasificadora(models.Model):
    _name = 'sigmap.sociedad.clasificadora'
    _description = _('Sociedad Clasificadora')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Nombre'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    codigo = fields.Char(
        string=_('Código'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_('Activo?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique')),
        ('code_uniq', 'unique (codigo)',
            _('The code must be unique'))
    ]
