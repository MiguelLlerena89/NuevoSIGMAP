import logging
from odoo import models, fields, api
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date, datetime

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    bank = fields.Selection(
        [('pacifico', 'Banco Pacifico'),
         ('pichincha', 'Banco Pichincha'),
         ('ruminahui', 'Banco Rumiñahui')],
        string='Banco',
        default='pacifico'
    )
    payment_code = fields.Char(string='Código de Papeleta')
    payment_date = fields.Date(string='Fecha de Depósito')
    sale_order_id = fields.Many2one('sale.order', 'Solicitud de trámites')
    confirmacion_automatica = fields.Boolean(
        related='payment_method_line_id.confirmacion_automatica',
        string="Confirmación automática",
    )
    forma_pago_id = fields.Many2one(
        related='payment_method_line_id.payment_method_id.forma_pago_id',
        string="Método de pago",
        store=True,
        readonly=False
    )
    sale_order_create_user_id = fields.Many2one("res.users", "Usuario", tracking=True)

    def create_payment(self):
        sale_order = self.env['sale.order'].browse(self._context.get('active_id'))

        fecha = self.payment_date
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
            if fecha > date.today():
                raise ValidationError('No puede ingresar un pago con una fecha futura.')
        payment = self.create({
            'payment_type': 'inbound',
            'partner_id': sale_order.partner_id.id,
            #'sale_order_id': sale_order.id,
            'sale_order_create_user_id': sale_order.create_uid.id,
            'forma_pago_id': self.forma_pago_id.id,
            'amount': self.amount,
            'bank': self.bank,
            'date': self.payment_date,
            'payment_date': self.payment_date,
            'payment_code': self.payment_code,
            'payment_method_line_id': self.payment_method_line_id.id,
            'ref': 'Codigo de Pago #%s' % sale_order.name, #TODO: Add parameter related to credit card payment
        })
        sale_order_payment = self.env['sale.order.payment'].create({
            'monto_abonado': payment.amount,
            'sale_id': sale_order.id,
            'payment_id': payment.id,
        })

        sale_order.write({'recaudacion_estado': 'RECAUDADO'})
        if payment.confirmacion_automatica:
            payment.action_post()
            #sale_order.action_done()
            #sale_order.write({'recaudacion_estado': 'RECAUDADO Y CONFIRMADO'})

        return {'type': 'ir.actions.act_window_close'}
