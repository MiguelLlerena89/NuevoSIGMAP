from odoo import api, fields, models, _

class NaveFotoTipo(models.Model):
    _name = 'nave.nave.foto.tipo'

    name = fields.Char(
        string=_('Name'),
        required=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_('Active?'),
        copy=False,
        tracking=True,
        default=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)',
            _('The name must be unique'))
    ]


class NaveFoto(models.Model):
    _name = 'nave.nave.foto'
    _description = _('Ship Picture')

    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Ship'),
        required=True,
        copy=False)

    tipo_foto_id = fields.Many2one(
        'nave.nave.foto.tipo',
        string=_('Type'),
        required=True,
        copy=False)

    fecha_foto = fields.Date(
        string=_('Picture Date'),
        required=True,
        copy=False)

    foto_1920 = fields.Image(
        string=_("Picture"),
        max_width=1920,
        max_height=1920)

    foto_128 = fields.Image(
        string=_("Picture"),
        related="foto_1920",
        max_width=128,
        max_height=128,
        store=True)

    active = fields.Boolean(
        string=_("Active?"),
        default=True)


class Nave(models.Model):
    _inherit = 'nave.nave'

    foto_ids = fields.One2many(
        'nave.nave.foto',
        'nave_id',
        string=_('Pictures'))
