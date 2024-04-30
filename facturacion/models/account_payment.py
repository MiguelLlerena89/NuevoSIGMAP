from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date, datetime

class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _default_sesion_caja(self):
        if 'default_move_type' in self.env.context:
            if self.env.context['default_move_type'] not in ('out_invoice', 'out_refund', 'entry'):
                return False
        user = self.env.user
        caja = self.env['sigmap.facturador'].search([('user_id', '=', user.id), ('active', '=', True), ('abierta', '=', True)], limit=1)
        if not caja:
            raise ValidationError('No hay caja abierta')
        sesion_caja_id = self.env['facturacion.sesion.caja'].search([
            ('caja_id', '=', caja.id),
            ('fecha_apertura', '!=', False),
            ('fecha_cierre', '=', False),
            ])
        if not sesion_caja_id:
            raise ValidationError('No hay caja abierta')
        return sesion_caja_id

    sesion_caja_id = fields.Many2one("facturacion.sesion.caja", "Sesión de caja", default=_default_sesion_caja)
    caja_id = fields.Many2one(related="sesion_caja_id.caja_id")
    sri_establecimiento_id = fields.Many2one(related='caja_id.sri_establecimiento_id')
    sri_punto_emision_id = fields.Many2one(related='caja_id.sri_punto_emision_id')
    # Pendiente calcular montos parciales pagados
    monto_disponible = fields.Monetary(string='Monto disponible', tracking=True, compute="_get_monto_disponible")

    @api.depends('order_ids')
    def _get_monto_disponible(self):
        for payment in self:
            disponible = sum(d['monto_abonado'] for d in self.order_ids)
            payment.monto_disponible = payment.amount - disponible

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'date' in vals:
                fecha = vals['date']
                if isinstance(fecha, str):
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
                if fecha > date.today():
                    raise ValidationError('No puede ingresar un pago con una fecha futura.')
        return super().create(vals_list)

    #def action_post(self):
    #    super().action_post()
    #    if self.state == 'posted':
    #        sale = self.sale_order_id
    #        if sale:
    #            factura = sale.action_confirm()
    #            if factura:
    #                receivable_line = self.line_ids.filtered('credit')
    #                factura.js_assign_outstanding_line(receivable_line.id)
