from odoo import fields, models, _

import logging

_logger = logging.getLogger(__name__)


class Sumilla(models.Model):
    _name = 'sigmap.sumilla'
    _description = 'Sumilla'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reparto_id = fields.Many2one('sigmap.reparto', required=True)

    responsable_delegado_id = fields.Many2one('res.users', string='Responsable delegado')

    responsable_ids = fields.One2many('sigmap.sumilla.responsable', 'sumilla_id', string='Responsables')

    active = fields.Boolean(_('Active?'), default=True)


class SumillaResponsable(models.Model):
    _name = 'sigmap.sumilla.responsable'

    sumilla_id = fields.Many2one('sigmap.sumilla')
    user_id = fields.Many2one('res.users', string='Responsable')
    sequence = fields.Integer(default=1)
    sumilla = fields.Char(related='user_id.sumilla')
