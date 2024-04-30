from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class NaveNave(models.Model):
    _inherit = 'nave.nave'

    #MOTORES FUERA DE BORDA
    motors_ids = fields.One2many('trafico.maritimo.motor', 'nave_id', string=_("Motors"))

class TraficoMaritimoNavegacion(models.Model):
    _inherit = 'trafico.maritimo.navegacion'

    #MOTORES FUERA DE BORDA
    motors_zarpe_ids = fields.One2many('trafico.maritimo.motor', 'trafico_maritimo_navegacion_id', string=_("Tráfico Marítimo Motores Fuera de Borda"))

class TraficoMaritimoMotorList(models.Model):
    _name = 'trafico.maritimo.motor'
    _description = "Motores"

    trafico_maritimo_navegacion_id = fields.Many2one('trafico.maritimo.navegacion', string=_("Tráfico Marítimo Navegación"), rondelete='cascade', index=True, copy=False)
    nave_id = fields.Many2one('nave.nave', string=_("Nave"), rondelete='cascade', index=True, copy=False, tracking=True)
    codigo_motor = fields.Char(string=_('Código Motor'), index=True, tracking=True)
    codigo_troquelado = fields.Char(string=_('Código Troquelado'), index=True, tracking=True)
    tipo_marca = fields.Char(string=_('Motor Brand'), index=True, tracking=True)
    tipo_motor = fields.Selection([
        ('fuera_borda', 'Fuera de Borda'),
        ('dentro_borda', 'Dentro de Borda'),
    ], string=_('Motor Type'), default='fuera_borda', index=True, copy=False, tracking=True)
    serie = fields.Char(string=_('Serie'), index=True, tracking=True)
    modelo = fields.Char(string=_('Motor Model'), index=True, tracking=True)
    velocidad = fields.Integer(string=_('Speed'), index=True, tracking=True)
    potencia = fields.Integer(string=_('Power'), index=True, tracking=True)
    propietario = fields.Many2one('nave.nave.propietario', string=_('Propietario'))
    active = fields.Boolean(string=_("Active?"), default=True, tracking=True)
