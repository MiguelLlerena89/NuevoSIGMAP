from odoo import api, fields, models, _

class NaveCanalBanda(models.Model):
    _name = 'nave.canal.banda'

    name = fields.Char(
        string=_('Name'),
        required=True,
        copy=False,
        tracking=True)

    tipo = fields.Selection(
        [
            ('vhf', 'VHF')
        ],
        string=_('tipo'))

    active = fields.Boolean(
        string=_('Active?'),
        copy=False)


class NaveCanal(models.Model):
    _name = 'nave.canal'

    name = fields.Char(
        string=_('Name'),
        required=True,
        copy=False)

    banda_id = fields.Many2one(
        'nave.canal.banda',
        string=_('Banda'),
        required=True,
        copy=False)
    
    banda_tipo = fields.Selection(
        related='banda_id.tipo',
        string=_('Banda')) 

    precio = fields.Float(string=_('Price'))

    active = fields.Boolean(
        string=_('Active?'),
        copy=False,
        default=True)


class NaveFrecuencia(models.Model):
    _name = 'nave.frecuencia'

    frecuencia = fields.Float(
        string=_('Frecuencia'),
        required=True,
        digits = (12,3))

    unidad = fields.Selection([
        ('mhz', 'MHz')
    ], string=_('Unidad'),
    default='mhz')

    tipo = fields.Selection([
        ('tx', 'Tx'),
        ('rx', 'Rx')
    ], string=_('Tipo'))

    canal_id = fields.Many2one(
        'nave.canal',
        string=_('Canal'))


class NaveCanal(models.Model):
    _inherit = 'nave.canal'

    frecuencia_ids = fields.One2many(
        'nave.frecuencia',
        'canal_id',
        string=_('frecuencias'))
