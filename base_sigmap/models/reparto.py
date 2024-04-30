from odoo import fields, models, _


class Reparto(models.Model):
    _name = 'sigmap.reparto'
    _description = _('Reparto')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Name'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    siglas = fields.Char(
        string=_('Siglas'),
        #required=True,
        index=True,
        copy=False,
        tracking=True)

    tipo_id = fields.Many2one(
        'sigmap.reparto.tipo',
        ondelete='restrict',
        string='Tipo reparto',
        #required=True,
        tracking=True)

    codigo_matricula = fields.Char(
        string='Código - Matrícula Nave',
        size=2,
        tracking=True)

    codigo_troquelado = fields.Char(
        string='Código - Troquelado Motor',
        size=2,
        tracking=True)

    puerto_id = fields.Many2one(
        'sigmap.puerto',
        string='Puerto',
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
            _('The name must be unique')),
        ('siglas_uniq', 'unique (siglas)',
            _('La sigla debe ser única'))
    ]
