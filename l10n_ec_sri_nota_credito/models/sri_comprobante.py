# -*- coding: utf-8 -*-

import os

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError, ValidationError, except_orm

class SRIComprobante(models.Model):

    _inherit = 'l10n_ec.sri.comprobante'

    def _get_report_data_04(self):
        return 'account.account_invoices', self.move_id.id

    def _info_comprobante_04(self):
        data = {}
        data.update(self._info_04())
        data.update(self._detalles())
        data.update(self._getAditionalInfo())

        return data, os.path.join(os.path.dirname(__file__), 'templates/out_refund.xml')

    def _info_04(self):

        info_comprobante = super()._info()

        if self.move_id.move_type == 'out_refund':
            inv = self.move_id.reversed_entry_id
            inv_number = '{0}-{1}-{2}'.format(inv.sri_establecimiento, inv.sri_punto_emision, inv.secuencial.zfill(9))  # noqa
            notacredito = {
                    'codDocModificado': inv.sri_autorizacion_id.l10n_latam_document_type_id.code,
                    'numDocModificado': inv_number,
                    'motivo': self.numero,
                    'fechaEmisionDocSustento': inv.invoice_date.strftime('%d/%m/%Y'),
                    'valorModificacion': self.move_id.amount_total
                    }
            info_comprobante.update(notacredito)
        return info_comprobante

