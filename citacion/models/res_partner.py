from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    multa_ids = fields.One2many(
        'citacion.multa',
        'contraventor_id',
        string=_('Penalties'))

    def _get_multas_a_pagar(self):
        self.ensure_one()
        if not self.multa_ids:
            return []
        else:
            multas_activas = []
            for penalty in self.multa_ids:
                if penalty.state == 'to_pay':
                    multas_activas.append(dict(
                        multa_id=penalty.id,
                        product_id=penalty.product_id.id,
                        description=penalty.description,
                        value=penalty.value
                    ))
            return multas_activas

    def _pagar_multas(self, paid_multa_ids=[], reversar=False, factura_id=None):
        self.ensure_one()
        for penalty in self.multa_ids:
            if penalty.id in paid_multa_ids:
                if not reversar and penalty.state == 'to_pay':
                    penalty.state = 'paid'
                    penalty.factura_id = factura_id
                if reversar and penalty.state == 'paid':
                    penalty.state = 'to_pay'
                    penalty.factura_id = False
