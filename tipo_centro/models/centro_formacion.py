from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)


class CentroFormacion(models.Model):
    _name = 'centro.formacion'
    _description = 'Centro Formacion'
    #_order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(_('Descripción'), required=1)
    siglas = fields.Char(string='Siglas', required=1)
    country_id = fields.Many2one('res.country', string='País Formación', tracking=True)
    active = fields.Boolean(_('Active?'), default=True)
    lugar_formacion_ids = fields.One2many('lugar.formacion', 'centro_id', 'Lugar Formación', tracking=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name, country_id)',
            'El centro de formación debe ser único')
    ]


class LugarFormacion(models.Model):
    _name = 'lugar.formacion'
    _description = 'Lugar de Formacion'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    centro_id = fields.Many2one('centro.formacion', string='Centro', tracking=True)
    city_id = fields.Many2one('res.city', string='Lugar Formación', tracking=True)
    active = fields.Boolean(_('Active?'), default=True)

    def name_get(self):
        res = []
        for rec in self:
            name = "%s / %s" % (rec.centro_id.name, rec.city_id.name)
            res.append((rec.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args = [('city_id.name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    _sql_constraints = [
        ('centro_city_uniq', 'unique (centro_id, city_id)',
            'El lugar de formación debe ser único')
    ]
