from odoo import api, fields, models, _

class TipoPropulsion(models.Model):
    _name = 'nave.tipo.propulsion'
    _description = _('Propulsion Type')

    name = fields.Char(
        string=_('Name'),
        required=True,
        index=True)

    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique'))
    ]
