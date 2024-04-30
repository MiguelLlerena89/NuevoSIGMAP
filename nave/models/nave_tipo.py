from odoo import api, fields, models, _

class NaveTipo(models.Model):
    _name = 'nave.nave.tipo'
    _description = _('Ship Type')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Name'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    codigo = fields.Char(
        string=_('Code'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    grupo_nave_id = fields.Many2one('nave.nave.grupo',
        string=_('Grupo Nave'),
        #required=True,
        index=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_("Active?"),
        default=True,
        tracking=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique')),
        ('code_uniq', 'unique (codigo)',
            _('The code must be unique'))
    ]
