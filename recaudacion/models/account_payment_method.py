from odoo import api, models, fields


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['dirnea_deposito'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        res['dirnea_transferir'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        res['dirnea_cheque'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        res['dirnea_appmovil'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        return res


class AccountPaymentMethodLine(models.Model):
    _inherit = 'account.payment.method.line'

    confirmacion_automatica = fields.Boolean(string="Confirmación automática", default=False)