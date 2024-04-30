from odoo import api, fields, models, _

class Periodo(models.Model):
    _name = 'sigmap.periodo'
    _description = _('Período')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc, anio_ini desc, fecha_ini desc'

    name = fields.Char(
        string=_('Período'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    anio_ini = fields.Integer(
        string=_('Año inicio'),
        index=True,
        copy=False,
        tracking=True)

    anio_fin = fields.Integer(
        string=_('Año fin'),
        index=True,
        copy=False,
        tracking=True)

    fecha_ini = fields.Date(
        string=_('fecha inicio'),
        index=True,
        copy=False,
        tracking=True)

    fecha_fin = fields.Date(
        string=_('fecha fin'),
        index=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_("Activo?"),
        default=True,
        index=True,
        copy=False,
        tracking=True)
