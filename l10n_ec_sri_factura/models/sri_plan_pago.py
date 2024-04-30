# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import itertools

class SRIPlanPago(models.Model):
    _name = "l10n_ec.sri.plan.pago"

    def _get_uom_domain(self):
        ids = self.env.ref('uom.uom_categ_wtime').ids
        return [('category_id', 'in', ids)]

    move_id = fields.Many2one('account.move', 'Movimiento')
    type_id = fields.Many2one('sri.payment.type', 'Tipo')
    forma_pago_id = fields.Many2one('l10n_ec.sri.payment')
    #forma_pago_id = fields.Many2one(related='type_id.forma_pago_id')
    plazo = fields.Integer(string='Plazo', index=True, copy=False)
    codigo_documento = fields.Char(string='Código documento', index=True, copy=False)
    banco = fields.Many2one('res.bank', 'Banco')
    total = fields.Float(string='Valor', store=True, copy=False)
    unidad_tiempo_id = fields.Many2one('uom.uom', domain=_get_uom_domain, string='Tiempo', index=True, copy=False)

    '''
    @api.onchange('forma_pago_id')
    def _onchange_forma_pago_id(self):
        if self.move_id.move_type in ('out_invoice'):
            if self.move_id.invoice_payment_term_id:
                self.plazo = self.move_id.invoice_payment_term_id.line_ids[0].days
            if self.move_id.amount_total != 0.0:
                self.total = self.move_id.amount_total
            else:
                return {
                    'warning': {
                        'title': _('Warning!'),
                        'message': _('Debe asignar producto(s)'),
                    }
                }
    '''

