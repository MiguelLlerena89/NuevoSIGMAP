# -*- coding: utf-8 -*-

from odoo import _
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import except_orm, ValidationError


class FacturacionSesionCajaWizard(models.TransientModel):
    _name = 'facturacion.sesion.caja.wizard'
    _description = 'Sesión de caja'

    def _default_caja(self):
        user = self.env.user
        caja = self.env['sigmap.facturador'].search([('user_id', '=', user.id)], limit=1)
        return caja

    caja_id = fields.Many2one("sigmap.facturador", "Caja", default=_default_caja, required=True)
    user_id = fields.Many2one(related='caja_id.user_id')
    abierta = fields.Boolean(related="caja_id.abierta")
    # Agregar fecha y hora de apertura de caja
    registro_caja = fields.Many2one("facturacion.sesion.caja",compute='_compute_caja_abierta')
    fecha_apertura = fields.Datetime(related='registro_caja.fecha_apertura')
    fecha_cierre = fields.Datetime()
    valor_apertura = fields.Float("Valor apertura", default=0)
    valor_cierre = fields.Float("Valor cierre", compute="_compute_get_valores")

    @api.depends('caja_id')
    def _compute_caja_abierta(self):
        if self.caja_id.abierta:
            caja = self.env['facturacion.sesion.caja'].search([
                ('caja_id', '=', self.caja_id.id),
                ('fecha_apertura', '!=', False),
                ('fecha_cierre', '=', False),
                ])
            self.registro_caja = caja.id
        else:
            self.registro_caja = False

    @api.depends('caja_id')
    def _compute_fecha_apertura(self):
        if self.registro_caja:
            self.fecha_apertura = self.registro_caja.fecha_apertura
        else:
            self.fecha_apertura = False

    @api.depends("caja_id", "fecha_apertura", "fecha_cierre")
    def _compute_get_valores(self):
        if not self.caja_id.abierta:
            self.valor_cierre = 0
        else:
            self.valor_cierre = 0

    def registrar(self):
        self.ensure_one()
        caja = self.caja_id
        if not caja.abierta and not self.registro_caja:
            data = {
                'caja_id': caja.id,
                'valor_apertura': self.valor_apertura,
                'fecha_apertura': fields.Datetime.today(),
            }
            valores = self.env['facturacion.sesion.caja'].create(data)
            if valores:
                caja.write({
                    'abierta': True
                })
        else:
            self.registro_caja.write({
                'valor_cierre': self.valor_cierre,
                'fecha_cierre': fields.Datetime.today(),
            })
            caja.abierta = False

        action = self.env["ir.actions.actions"]._for_xml_id("facturacion.action_view_facturacion_sesion_caja_wizard_form")
        action.update({
            'res_id': self.registro_caja.id,
        })
        return action


