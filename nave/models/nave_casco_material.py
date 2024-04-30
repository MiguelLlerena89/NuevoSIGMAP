from odoo import api, fields, models, _

class NaveCascoMaterial(models.Model):
    _name = 'nave.casco.material'
    _description = _( 'Hull Material')

    name = fields.Char(
        string=_('Description'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique'))
    ]
