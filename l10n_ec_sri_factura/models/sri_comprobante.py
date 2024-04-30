# -*- coding: utf-8 -*-

import os
import itertools

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError, ValidationError

class SRIComprobante(models.Model):

    _inherit = 'l10n_ec.sri.comprobante'

    move_id = fields.Many2one('account.move', copy=False)

    def _get_report_data_01(self):
        return 'account.account_invoices', self.move_id.id

    def _info_comprobante_01(self):
        data = {}
        data.update(self._info())
        data.update(self._getAditionalInfo())
        detalles = self._detalles()
        data.update(detalles)
        data.update(self._compute_discount(detalles))

        return data, os.path.join(os.path.dirname(__file__), 'templates/out_invoice.xml')

    def _info(self):
        """
        """

        company = self.company_id
        partner = self.partner_id
        move = self.move_id
        plazo = ''
        info_comprobante = {}

        info_comprobante.update({
            'fechaEmision': move.invoice_date.strftime('%d/%m/%Y'),
            'dirEstablecimiento': company.street,
            'obligadoContabilidad': 'SI' if company.obligado_contabilidad else 'NO',
            'tipoIdentificacionComprador': partner.l10n_latam_identification_type_id.l10n_ec_sri_code,  # noqa
            'razonSocialComprador': partner.name,
            'identificacionComprador': partner.vat,
            'totalSinImpuestos': '%.2f' % (move.amount_untaxed),
            'totalDescuento': '%.2f' % (move.total_descuento),
            'propina': '0.00',
            #'importeTotal': '{:.2f}'.format(move.amount_pay),
            'importeTotal': '{:.2f}'.format(move.amount_total),
            'moneda': 'DOLAR',
            'valorRetIva': '{:.2f}'.format(move.total_ret_iva),  # noqa
            'valorRetRenta': '{:.2f}'.format(move.total_ret_ir)
        })

        for plan in move.plan_pago_ids:
            plan_data = {
                    'unidadTiempo': plan.unidad_tiempo_id.name,
                    'plazo': plan.plazo,
                    'formaPago': plan.forma_pago_id.code,
                    'importeTotal': '{:.2f}'.format(plan.total),
            }
            if 'planPagos' not in info_comprobante:
                info_comprobante['planPagos'] = [plan_data]
            else:
                info_comprobante['planPagos'].append(plan_data)

        if company.contribuyente_especial:
            if company.resolucion_contribuyente_especial:
                info_comprobante.update({'contribuyenteEspecial':
                                    company.resolucion_contribuyente_especial})
            else:
                raise UserError(_('No ha determinado si es contribuyente especial.'))

        if company.resolucion_agente_retencion:
            resolution = company.resolucion_agente_retencion.split('-')
            info_comprobante.update({'agenteRetencion': resolution[2]})  # noqa

        totalConImpuestos = []
        tax_list = []
        for line in move.invoice_line_ids:
            for tax_line in line.tax_ids:
                tax_list.append((tax_line, line.price_subtotal))

        for tax_id, tax_data in itertools.groupby(sorted(tax_list, key=lambda e: e[0].id), key=lambda e: e[0]):
            tax = list(tax_data)
            group_code = tax_id.tax_group_id.l10n_ec_type
            if group_code in ['vat12', 'zero_vat', 'ice']:
                detalleImpuesto = {
                    'codigo': tax_id.tax_group_id.l10n_ec_xml_fe_code,
                    'codigoPorcentaje': tax_id.l10n_ec_xml_fe_code,
                    'descuentoAdicional': '0.00',
                    'baseImponible': sum(e[1] for e in tax),
                    'tarifa': '{:d}'.format(abs(int(tax_id.amount))),
                    'valor': '%.2f' % (sum(e[0].amount * e[1]/100 for e in tax)),
                }

                totalConImpuestos.append(detalleImpuesto)
        if not totalConImpuestos:
            raise UserError(_('No se puede generar factura electrónica sin impuestos'))

        info_comprobante.update({'totalConImpuestos': totalConImpuestos})

        return info_comprobante

    def _detalles(self):
        """
        """
        detalles = []
        def fix_chars(code):
            special = [
                [u'%', ' '],
                [u'º', ' '],
                [u'Ñ', 'N'],
                [u'ñ', 'n'],
                [u'\n', ' ']
            ]
            for f, r in special:
                code = code.replace(f, r)
            return code

        move = self.move_id
        for line in move.invoice_line_ids:
            #TODO codigo no debe ser id
            codigoPrincipal = line.product_id.id
            priced = line.price_unit * (1 - (line.discount or 0.00) / 100.0)
            discount = (line.price_unit - priced) * line.quantity
            detalle = {
                'codigoPrincipal': codigoPrincipal,
                'descripcion': fix_chars(line.name.strip()),
                #'unidadMedida': fix_chars(line.uom_id.name.strip()),
                'cantidad': '%.6f' % (line.quantity),
                'precioUnitario': '%.6f' % (line.price_unit),
                'descuento': '%.2f' % discount,
                'precioTotalSinImpuesto': '%.2f' % (line.price_subtotal)
            }
            impuestos = []
            for tax_line in line.tax_ids:
                if tax_line.tax_group_id.l10n_ec_type in ['vat12', 'zero_vat', 'ice']:
                    impuesto = {
                        'codigo': tax_line.tax_group_id.l10n_ec_xml_fe_code,
                        'codigoPorcentaje': tax_line.l10n_ec_xml_fe_code,
                        'tarifa': tax_line.amount,
                        'baseImponible': '{:.2f}'.format(line.price_subtotal),
                        'valor': '{:.2f}'.format(line.price_subtotal * tax_line.amount/100),
                    }
                    impuestos.append(impuesto)
            detalle.update({'impuestos': impuestos})
            detalles.append(detalle)
        return {'detalles': detalles}

    def _compute_discount(self, detalles):
        total = sum([float(det['descuento']) for det in detalles['detalles']])
        return {'totalDescuento': total}

    def _getAditionalInfo(self):
        #TODO correo obligatorio
        aditionals = [{
                'key': 'Correo', 'value': self.partner_id.email or 'NN'
                }]
        move = self.move_id
        for line in move.aditional_info_ids:
            aditionals.append({'key': line.adicional_nombre, 'value': line.adicional_valor})

        return {
            "_infoAdicional": aditionals }
