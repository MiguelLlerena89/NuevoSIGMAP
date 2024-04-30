# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    state = fields.Selection(
        selection=[
            ('draft', 'No confirmado'),
            ('posted', 'Confirmado'),
            ('cancel', 'Anulado'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )

    def _default_sesion_caja(self):
        if 'default_move_type' in self.env.context:
            if self.env.context['default_move_type'] not in ('out_invoice', 'out_refund', 'entry'):
                return False
        user = self.env.user
        check_usuario_caja = self.env['sigmap.facturador'].search([('user_id', '=', user.id), ('active', '=', True)], limit=1)
        caja = self.env['sigmap.facturador'].search([('user_id', '=', user.id), ('active', '=', True), ('abierta', '=', True)], limit=1)
        if not check_usuario_caja:
            raise ValidationError('No tiene asignada una caja')
        if not caja:
            raise ValidationError('No hay caja abierta')
        sesion_caja = self.env['facturacion.sesion.caja'].search([
            ('caja_id', '=', caja.id),
            ('fecha_apertura', '!=', False),
            ('fecha_cierre', '=', False),
            ])
        return sesion_caja

    sesion_caja_id = fields.Many2one("facturacion.sesion.caja", "Sesión de caja", default=_default_sesion_caja)
    caja_id = fields.Many2one(related="sesion_caja_id.caja_id")
    sri_establecimiento_id = fields.Many2one(related='caja_id.sri_establecimiento_id')
    sri_punto_emision_id = fields.Many2one(related='caja_id.sri_punto_emision_id')

    @api.depends('invoice_line_ids.product_id')
    def _create_informacion_adicional_line_values(self):
        for rec in self:
            if rec.move_type in ('out_invoice'):
                inf_addicional = []
                for line in rec.invoice_line_ids:
                    data = {}
                    if line.product_id:
                        if line.product_id.product_tmpl_id.articulo and line.product_id.product_tmpl_id.numeral:
                            valor = 'Art.' + line.product_id.product_tmpl_id.articulo + ' Numeral.' + line.product_id.product_tmpl_id.numeral + ' '
                            if line.product_id.product_tmpl_id.tipo_documento_id:
                                valor += line.product_id.product_tmpl_id.tipo_documento_id.name
                            data = {
                                'adicional_nombre': line.product_id.name,
                                # Agregar tipo de documento
                                'adicional_valor': valor,
                                }
                        else:
                            data = {
                                'adicional_nombre': 'Trámite',
                                'adicional_valor': line.product_id.name,
                                }
                    else:
                        data = {
                            'adicional_nombre': 'Trámite',
                            'adicional_valor': line.product_id.name,
                            }
                    inf_addicional.append((0, 0, data))
                rec.write({'aditional_info_ids': inf_addicional})
            else:
                rec.aditional_info_ids = False

    @api.depends('invoice_line_ids','invoice_payment_term_id')
    def _create_default_plan_pago_line_values(self):
        for rec in self:
            if rec.move_type in ('out_invoice'):
                if rec.amount_total != 0:
                    plazo = rec.invoice_payment_term_id.line_ids[0].days if rec.invoice_payment_term_id else 0
                    data = {
                            # Ver qué forma de pago usar?
                            'forma_pago_id': self.env.ref('l10n_ec.P20').id,
                            'plazo': plazo,
                            'total': rec.amount_total,
                            'unidad_tiempo_id': self.env.ref('uom.product_uom_day').id,
                            }
                    rec.write({'plan_pago_ids': [(0, 0, data)]})
                else:
                    rec.plan_pago_ids = False
            else:
                rec.plan_pago_ids = False

    def action_post(self):
        if self.move_type not in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'):
            return super().action_post()

        if not self.caja_id.abierta:
            raise UserError(_("Confirmar registro: No puede facturar, no hay caja abierta."))

        return super().action_post()

    def write(self, vals):
        if self.move_type not in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'):
            return super().write(vals)
        if not self.caja_id.abierta:
            raise UserError(_("Escritura: No puede facturar, no hay caja abierta."))
        elif self.invoice_date < fields.Date.today():
            raise UserError(_("No puede editar facturas pasadas."))
        else:
            return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Pendiente verificar si es una factura antes de crear
            if 'move_type' in vals:
                if vals['move_type'] not in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'):
                    break
                if vals['move_type'] in ['entry']:
                    break
            if 'sesion_caja_id' in vals:
                caja = self.env['facturacion.sesion.caja'].browse(vals['sesion_caja_id'])
                if not caja.caja_id.abierta:
                    raise UserError(_("Create: No puede facturar, no hay caja abierta."))
        return super().create(vals_list)

    def button_cancel(self):
        if self.move_type not in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'):
            super().button_cancel()
        elif not self.caja_id.abierta:
            raise UserError(_("Delete: No puede facturar, no hay caja abierta."))
        elif self.invoice_date < fields.Date.today():
            raise UserError(_("No puede editar facturas pasadas."))
        else:
            super().button_cancel()
        if self.comprobante_id:
            self.comprobante_id.state = 'NUL'

