from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class UomSuministro(models.Model):
    _name = 'uom.suministro'
    _description = 'Unidad de medida Suministro'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre', index=True, copy=False, tracking=True)
    codigo = fields.Char(string='Código', index=True, copy=False, tracking=True)
    unidades = fields.Float('Unidades')
    unidad_id = fields.Many2one('uom.suministro', string='Unidad de consumo', copy=False, tracking=True)
    #Cuántas unidades hay en esta unidad de medida


class Suministro(models.Model):
    _name = 'suministro'
    _description = 'Suministro'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', string='Company')
    name = fields.Char(string='Nombre', index=True, copy=False, tracking=True)
    descripcion = fields.Char(string='Descripción', copy=False, tracking=True)
    unidad_id = fields.Many2one('uom.suministro', string='Unidad de consumo', copy=False, tracking=True)
    cantidad_unidades = fields.Integer(string='Unidades disponibles', copy=False, tracking=True)


class ControlSuministro(models.Model):
    _name = 'control.suministro'
    _description = 'Control suministro'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)

    user_id = fields.Many2one('res.users', string='Responsable')
    name = fields.Char(string='Nombre', index=True, copy=False, tracking=True)
    suministro_id = fields.Many2one('suministro', string='Suministro')
    unidad_id = fields.Many2one('uom.suministro', string='Unidad de consumo', copy=False, tracking=True)
    cantidad = fields.Integer(string='Registro cantidad', copy=False, tracking=True, default=0)
    cantidad_unidades = fields.Integer(string='Cantidad en unidades', compute="_compute_cantidades", copy=False, tracking=True, default=0, store=True)
    fecha_entrega = fields.Date('Fecha entrega', tracking=True)
    fecha_ingreso = fields.Date(
        string="Fecha ingreso registro",
        index=True,
        copy=False,
        tracking=True,
        default=fields.Date.today
    )

    @api.depends("cantidad", "unidad_id")
    def _compute_cantidades(self):
        for control_suministro in self:
            control_suministro.cantidad_unidades = control_suministro.cantidad * control_suministro.unidad_id.unidades
            query = '''
                SELECT
                    SUM(cs.cantidad_unidades) AS cantidades_totales
                FROM control_suministro as cs
                WHERE suministro_id IN %s
            '''
            registros = self.env['control.suministro'].search([('suministro_id', '=', control_suministro.suministro_id.id)])
            params = [tuple(registros.ids)]
            self._cr.execute(query, params)

            ref = self._cr.dictfetchone()
            control_suministro.suministro_id.cantidad_unidades = ref['cantidades_totales']