from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def crear_factura(self):
        return self._create_invoices(final=True)

    def action_confirm(self):
        res = super().action_confirm()
        if self.state == "sale":
            factura = self._create_invoices(final=True)
            factura.action_post()
            return factura
        return res