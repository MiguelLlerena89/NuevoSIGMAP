from odoo import api, fields, models, _

class Resolucion(models.Model):
    _name = 'sigmap.resolucion'
    _description = _('Resolución')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Resolución'),
        required=True,
        index=True,
        copy=True,
        tracking=True)

    descripcion = fields.Char(
        string=_('descripcion'),
        required=True,
        index=False,
        copy=True,
        tracking=True)

    periodo_id = fields.Many2one(
        comodel_name='sigmap.periodo',
        string=_('Periodo'),
        required=True,
        index=True,
        copy=True,
        tracking=True)

    version = fields.Integer(
        string=_('version'),
        required=True,
        default=0,
        index=False,
        copy=True,
        tracking=True)

    active = fields.Boolean(
        string=_("Activo?"),
        required=True,
        default=True,
        index=False,
        copy=False,
        tracking=True)

    resolucion_file = fields.Binary(
        string=_('Resolución'),
        required=True,
        index=False,
        copy=False,
        tracking=True)

    resolucion_filename = fields.Char(
        string=_('Nombre archivo'),
        required=False,
        index=False,
        copy=False,
        tracking=True)
