from odoo import fields, models, _

import logging

_logger = logging.getLogger(__name__)


class InspectorTipo(models.Model):
    _name = 'sigmap.inspector.tipo'
    _description = 'Tipo Inspector'
    _order = 'orden'

    '''
    ID Orden Descripcion
    1	10	 Inspector de Naves Menores
    2	20	 Inspector de Naves Mayores
    3	30	 Inspector de Nuevas Construcciones
    4	40	 Supervisor de Estado Rector del Puerto
    5	50	 Inspector de Naves < 10 TRB
    14	60	 Inspector SMM
    '''

    orden = fields.Integer(_('Orden'))
    name = fields.Char(_('Name'))
    active = fields.Boolean(_('Active?'), default=True)


class Inspector(models.Model):
    _name = 'sigmap.inspector'
    _description = 'Inspector'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_res_users_inspector(self):
        return [('id', 'in', self.env.ref('usuarios.group_inspector').users.ids)]

    user_id = fields.Many2one('res.users', 'Usuario', required=True, domain=_get_res_users_inspector)

    '''
    tipo = fields.Selection(
        [
            ('naves_menores', 'Naves menores'),
            ('naves_mayores', 'Naves mayores'),
            ('estado_rector_puerto', 'Estado rector de puerto'),
        ],
        string=_('Tipo'))
    '''

    def _default_tipo_id(self):
        return self.env['sigmap.inspector.tipo'].search([], limit=1)

    tipo_id = fields.Many2one(
        comodel_name='sigmap.inspector.tipo',
        string=_('tipo'),
        required=True,
        default=_default_tipo_id)

    active = fields.Boolean(
        _('Active?'),
        default=True)

    name = fields.Char(related='user_id.name', string=_('Nombre'))
