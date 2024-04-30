from odoo import fields, models, api, _

import logging

_logger = logging.getLogger(__name__)


class Facturador(models.Model):
    _name = 'sigmap.facturador'
    _description = 'Facturador'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_res_users_facturador(self):
        return [('id', 'in', self.env.ref('usuarios.group_facturador').users.ids)]

    user_id = fields.Many2one('res.users', 'Usuario', required=True, domain=_get_res_users_facturador)

    reparto_id = fields.Many2one('sigmap.reparto', string=_('Reparto'), required=True, readonly=True,
                                 ondelete='restrict')
    company_id = fields.Many2one('res.company', string='Institución', required=True, readonly=True)

    caja = fields.Char('Número caja')
    sri_establecimiento_id = fields.Many2one(related="reparto_id.sri_establecimiento_id")
    establecimiento = fields.Char(related='sri_establecimiento_id.code')
    sri_punto_emision_id = fields.Many2one("l10n_ec.sri.punto.emision",
                                           domain="[('establecimiento_id', '=', sri_establecimiento_id)]")
    punto_emision = fields.Char(related='sri_punto_emision_id.code')

    fechahora_inicio = fields.Datetime('Inicio', default=fields.Datetime.now, readonly=True)
    fechahora_fin = fields.Datetime('Fin')

    active = fields.Boolean(_('Active?'), default=True)

    @api.onchange('user_id')
    def _onchange_partner(self):
        if self.user_id and self.user_id.reparto_id:
            self.reparto_id = self.user_id.reparto_id
            self.sri_establecimiento_id = self.user_id.reparto_id.sri_establecimiento_id

        if self.user_id and self.user_id.reparto_id and self.user_id.reparto_id.company_id:
            self.company_id = self.user_id.reparto_id.company_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            user = self.env['res.users'].browse(vals['user_id'])
            vals['reparto_id'] = user.reparto_id.id
            vals['company_id'] = user.reparto_id.company_id.id
            vals['establecimiento'] = user.reparto_id.establecimiento
        return super().create(vals_list)
