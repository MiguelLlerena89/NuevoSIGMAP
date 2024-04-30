
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import formataddr


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    motivo_cancelar_solicitud = fields.Text('Motivo de cancelar solicitud')


class SaleOrderCancel(models.TransientModel):
    _inherit = 'sale.order.cancel'

    motivo_cancelar_solicitud = fields.Text('Motivo de cancelar solicitud')

    def action_cancel(self):
        self.order_id.motivo_cancelar_solicitud = self.motivo_cancelar_solicitud
        return super(SaleOrderCancel, self).action_cancel()