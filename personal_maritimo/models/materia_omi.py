from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

import logging

_logger = logging.getLogger(__name__)

class CategoriaMateria(models.Model):

    _name = 'categoria.materia'
    _description = 'Categoria Materia'

    name = fields.Char(string='Descripción', required=True)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "La descripción de la categoria ya existe!"),
    ]


class MateriaOMI(models.Model):
    _name = 'materia.omi'
    _description = 'Materia o curso OMI'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Descripción', tracking=True)
    code = fields.Char(string='Código OMI', tracking=True)
    categoria_id = fields.Many2one('categoria.materia', string='Categoría OMI', tracking=True)
    active = fields.Boolean(_('Active?'), default=True)

    def name_get(self):
        self.read(['code'])
        return [(materia.id, 'OMI %s' % (materia.code))
            for materia in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            if operator in ('=', '!='):
                domain = ['|', ('code', '=', name.split(' ')[0]), ('name', operator, name)]
            else:
                domain = ['|', ('code', '=ilike', name.split(' ')[0] + '%'), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "El código OMI ya exsite!"),
    ]