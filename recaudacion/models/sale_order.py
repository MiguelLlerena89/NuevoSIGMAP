import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class SaleOrderPayment(models.Model):
    _name = 'sale.order.payment'

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    sale_id = fields.Many2one("sale.order", "Solicitud", tracking=True)
    monto_abonado = fields.Monetary(string='Monto abonado', tracking=True)
    payment_id = fields.Many2one("account.payment", "Pago", tracking=True)

    currency_id = fields.Many2one(related='payment_id.currency_id')
    state = fields.Selection(related='payment_id.state')

class Payment(models.Model):
    _inherit = 'account.payment'

    order_ids = fields.One2many("sale.order.payment", "payment_id", "SaleOrders", tracking=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_pagado = fields.Monetary(string='Total pagado', compute="compute_totales", store=True)
    payment_ids = fields.One2many("sale.order.payment", "sale_id", "Pagos", tracking=True)

    recaudacion_codigo = fields.Char(string='Código Recaudación', readonly=True)
    recaudacion_estado = fields.Selection([
        ('NO RECAUDADO', 'NO RECAUDADO'),
        ('RECAUDADO', 'RECAUDADO'),
        ('RECAUDADO Y CONFIRMADO', 'RECAUDADO CONFIRMADO'),
        ('ANULADO', 'ANULADO'),
    ], string='Estado Recaudacion',default='NO RECAUDADO', readonly=True)

    @api.depends('payment_ids', 'payment_ids.state')
    def compute_totales(self):
        self.total_pagado = sum(d['monto_abonado'] for d in self.payment_ids.filtered(lambda a: a.payment_id.state in ['posted']))
        if len(self.payment_ids) > 0:
            if self.total_pagado == self.amount_total:
                factura = self.action_confirm()
                self.recaudacion_estado = 'RECAUDADO Y CONFIRMADO'
                if factura:
                    for payment in self.payment_ids:
                        receivable_line = payment.payment_id.line_ids.filtered('credit')
                        factura.js_assign_outstanding_line(receivable_line.id)
                    self.action_done()

    def write(self, vals):
        recaudacion_codigo_reparto = "01" #Todo a los repartos hay que definir un codigo de reparto para recaudaciones
        for sale_order in self:
            if sale_order.state == 'sent':
                vals['recaudacion_codigo'] = str(fields.Date.today(self).year)[-2:] + recaudacion_codigo_reparto + "0" + str(self.name[1:])
                vals['recaudacion_estado'] = "NO RECAUDADO"

        _logger.info("Recaudacion data created: %s", vals)
        res = super().write(vals)
        return res

    def action_pagar_con_tarjeta(self):
        for sale_order in self:
            if sale_order.state == 'sent':
                payment = self.env['account.payment'].create({
                    'partner_id': sale_order.partner_id.id,
                    'amount': sale_order.amount_total,
                    #'sale_order_id': sale_order.id,
                    'payment_type': 'inbound',  # Tipo de pago: entrada
                    'ref': 'Codigo de Pago #%s' % sale_order.name, #TODO: Add parameter related to credit card payment
                })
                sale_order.write({'recaudacion_estado': 'RECAUDADO'})
                sale_order.action_confirm()

    def action_pagado(self):
        result = super().action_pagado()
        view_id = self.env.ref('recaudacion.sale_order_recaudacion_manual').id
        amount_total = self.amount_total - self.total_pagado
        ctx = {'default_amount': amount_total,}
        return {
            'name': 'Pago Manual',
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
        }
