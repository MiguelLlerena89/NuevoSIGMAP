from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    #guia_remision_id
    #retencion

    COMPROBANTE_TIPO = {
            'out_invoice': '01',
            'in_invoice': '01',
            'out_refund': '04',
            'in_refund': '04',
            }
    def _default_autorizacion(self):
        if self.env.context.get('default_move_type'):
            move_type = self.env.context['default_move_type']
            if move_type in ['out_invoice', 'out_refund']:
                code = self.COMPROBANTE_TIPO[move_type]
                auth = self.env['l10n_ec.sri.autorizacion'].search([('autorizacion_tipo', '=', 'out'), ('code','like', code), ('partner_id', '=', self.env.user.company_id.partner_id.id)], limit=1)
                return auth
            else:
                return False

    def _default_secuencial(self):
        if self.env.context.get('default_move_type'):
            move_type = self.env.context['default_move_type']
            if move_type in ['out_invoice', 'out_refund']:
                code = self.COMPROBANTE_TIPO[move_type]
                auth = self.env['l10n_ec.sri.autorizacion'].search([('autorizacion_tipo', '=', 'out'), ('code','like', code), ('partner_id', '=', self.env.user.company_id.partner_id.id)], limit=1)
                if auth:
                    return auth.sequence_id.number_next_actual
            else:
                return False

    secuencial = fields.Char(default=_default_secuencial)

    @api.depends('is_electronic', 'move_type', 'sri_establecimiento_id', 'sri_punto_emision_id')
    def _get_default_autorizacion(self, move_type):
        autorizacion = secuencial = False
        if self.is_electronic:
            if move_type in ['out_invoice','out_refund'] and self.sri_establecimiento_id and self.sri_punto_emision_id:
                code = self.COMPROBANTE_TIPO[move_type]
                domain = [('autorizacion_tipo', '=', move_type.split('_')[0]),('code','like', code),('establecimiento_id','=', self.sri_establecimiento_id.id),('punto_emision_id','=', self.sri_punto_emision_id.id)]
                if move_type.startswith('out_'):
                    partner = self.company_id.partner_id.id
                else:
                    partner = self.partner_id.id
                domain_partner= ('partner_id', '=', partner)
                domain.append(domain_partner)
                autorizacion_id = self.env['l10n_ec.sri.autorizacion'].search(domain)
                if autorizacion_id:
                    autorizacion = autorizacion_id.id
                else:
                    raise UserError(_('No existe autorización de nota de crédito para establecimiento: %s y punto de emisión: %s') % (self.sri_establecimiento_id.code, self.sri_punto_emision_id.code))
                if self.move_type.startswith('out_'):
                    secuencial = autorizacion_id.sequence_id.number_next_actual
        return autorizacion, secuencial

    def _reverse_moves(self, default_values_list=None, cancel=False):
        reverse_type_map = {
            'entry': 'entry',
            'out_invoice': 'out_refund',
            'out_refund': 'entry',
            'in_invoice': 'in_refund',
            'in_refund': 'entry',
            'out_receipt': 'entry',
            'in_receipt': 'entry',
        }
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            autorizacion, secuencial = move._get_default_autorizacion(reverse_type_map[move.move_type])
            default_values.update({
                'sri_autorizacion_id': autorizacion,
                'secuencial': secuencial,
            })
        return super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)