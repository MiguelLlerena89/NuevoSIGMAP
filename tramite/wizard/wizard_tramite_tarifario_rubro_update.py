# -*- coding: utf-8 -*-

from odoo import _
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import except_orm, ValidationError


class WizardTarifarioUpdateRubro(models.TransientModel):
    _name = 'tramite.tarifario.rubro.update.wizard'
    _description = 'Actualización de valores en rubros'

    indice_inflacion = fields.Float("Índice inflación", required=True)
    year = fields.Integer("Año", required=True)
    tarifario_id = fields.Many2one("tramite.tarifario", "Tarifario", required=True)
    fecha_desde = fields.Datetime(
        string="Fecha desde",
        tracking=True,
    )
    fecha_hasta = fields.Datetime(
        string="Fecha hasta",
        tracking=True,
    )

    def calcular_nuevos_valores(self):
        self.ensure_one()
        if self.indice_inflacion < 0:
            return
        for rubro in self.tarifario_id.rubro_ids:
            if rubro.producto_id.incremento_anual:
                # Revisar si existe tarifas para este rubro
                # Revisar si existen tarifas anteriores con incremento
                # usar ese valor y calcular el incremento
                tarifas = self.env['rubro.tarifa'].search(
                    [
                        ('tarifario_id', '=', self.tarifario_id.id),
                        ('rubro_id', '=', rubro.producto_id.id),
                        ('active', '=', True)
                    ]
                )
                if tarifas:
                    for tarifa in tarifas:
                        valor_anterior = self.env['rubro.tarifa.valor'].search(
                            [
                                ('rubro_tarifa_id', '=', tarifa.id),
                                ('active', '=', True)
                            ]
                        )
                        if valor_anterior:
                            monto_anterior = valor_anterior.monto
                            inflacion = valor_anterior.monto * self.indice_inflacion / 100
                            monto = monto_anterior + inflacion
                            valor_anterior.active = False
                        else:
                            monto_anterior = 0
                            monto = tarifa.monto
                        data = {
                            'rubro_tarifa_id': tarifa.id,
                            'incremento': self.indice_inflacion,
                            'valor_anterior': monto_anterior,
                            'monto': monto,
                            'year': self.year,
                            'fecha_desde': self.fecha_desde,
                            'fecha_hasta': self.fecha_hasta,
                        }
                        valores = self.env['rubro.tarifa.valor'].create(data)

