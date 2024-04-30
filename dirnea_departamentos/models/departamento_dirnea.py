from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)


class DepartamentoDirnea(models.Model):
    _name = 'departamento.dirnea'
    _description = 'Departamento DIRNEA'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(_('Descripción'), required=1)
    codigo = fields.Char(_('Código'), required=1)
    director_id = fields.Many2one('res.users', string="Director", tracking=True, copy=False)
    subdirector_id = fields.Many2one('res.users', string="Subdirector", tracking=True, copy=False)
    jefe_area_id = fields.Many2one('res.users', string="Jefe área", tracking=True, copy=False)

    personal_ids = fields.One2many('departamento.dirnea.line', 'departamento_id', string="Usuarios", tracking=True, copy=False)

class DepartamentoDirneaLine(models.Model):
    _name = 'departamento.dirnea.line'
    _description = 'Departamento DIRNEA'

    personal_id = fields.Many2one('res.users', string="Usuario", tracking=True, copy=False)
    departamento_id = fields.Many2one('departamento.dirnea', string="Departamento", tracking=True, copy=False)