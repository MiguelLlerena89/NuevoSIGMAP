from odoo import api, fields, models, _
import json

class SancionadoAyuda(models.Model):
    _name = 'citacion.sancionado.ayuda'


    articulo_id = fields.Many2one(
        'citacion.contravencion.ley.art',
        string=_('Article'))

    articulo_description = fields.Char(
        string=_('Description'),
        related='articulo_id.description')

    numeral_id_domain = fields.Char(
        string=_('numeral_id domain'),
        compute='_compute_numeral_id_domain',
        store=True,
        precompute=True)

    numeral_id = fields.Many2one(
        'citacion.contravencion.ley.num',
        string=_('Numeral'))

    numeral_description = fields.Char(
        string=_('Description'),
        related='numeral_id.description')

    capitan = fields.Boolean(
        string=_('Captain'),
        default=True)

    tripulante = fields.Boolean(string=_('Crew Member'))

    armador = fields.Boolean(string=_('Charterer'))

    propietario = fields.Boolean(string=_('Owner'))


    @api.depends('articulo_id')
    def _compute_numeral_id_domain(self):
        for rec in self:
            articulo_id = rec.articulo_id.id if rec.articulo_id else False
            rec.numeral_id_domain = json.dumps([
                ('articulo_id', '=', articulo_id)
            ])

    @api.onchange('numeral_id')
    def _onchange_numeral_id(self):
        num = self.numeral_id
        if num and num.articulo_id != self.articulo_id:
            self.articulo_id = num.articulo_id

    @api.onchange('articulo_id')
    def _onchange_articulo_id(self):
        num = self.numeral_id
        if num and num.articulo_id != self.articulo_id:
            self.numeral_id = False
