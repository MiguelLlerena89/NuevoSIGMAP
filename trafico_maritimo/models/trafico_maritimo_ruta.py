from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class TraficoMaritimoRuta(models.Model):
    _name = 'trafico.maritimo.ruta'
    _description = "Ruta"

    name = fields.Char(string='Nombre', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string=_('Company'), required=True, index=True, default=lambda self: self.env.company.id)
    user_id = fields.Many2one(
        'res.users', string=_('User'), index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    active = fields.Boolean(string=_("Active?"), default=True, tracking=True)
    ruta_geocoordenada_ids = fields.One2many('trafico.maritimo.ruta.geocoordenada', 'trafico_maritimo_ruta_id', string=_("Tráfico Marítimo Ruta"))


class TraficoMaritimoRutaGeocoordenada(models.Model):
    _name = 'trafico.maritimo.ruta.geocoordenada'
    _description = "Ruta Geocoordenada"

    trafico_maritimo_ruta_id = fields.Many2one('trafico.maritimo.ruta', string=_("Tráfico Marítimo Ruta"), ondelete='cascade', index=True, copy=False)
    orden = fields.Integer(string=_('Orden'))
    latitud = fields.Float(string='Latitud', digits=(10, 7), store=True)
    longitud = fields.Float(string='Longitud', digits=(10, 7), store=True)
    latitud_dms = fields.Char(string='Latitud DMS', readonly=True)
    longitud_dms = fields.Char(string='Longitud DMS', readonly=True)


class TraficoMaritimoNavegacion(models.Model):
    _inherit = 'trafico.maritimo.navegacion'

    #Rutas
    ruta_ids = fields.One2many('trafico.maritimo.navegacion.ruta', 'trafico_maritimo_navegacion_id', string=_("Tráfico Marítimo Ruta"))

class TraficoMaritimoNavegacionRuta(models.Model):
    _name = 'trafico.maritimo.navegacion.ruta'
    _description = "Lineas de Rutas"
    _inherit = 'trafico.maritimo.ruta.geocoordenada'

    trafico_maritimo_navegacion_id = fields.Many2one('trafico.maritimo.navegacion', string=_("Tráfico Marítimo Navegación"), ondelete='cascade', index=True, copy=False)
    ultimo_evento = fields.Selection([
        ('P', 'Plan de viaje (previo arribo/zarpe)'),
        ('QTH', 'Qth'),
    ], string=_('Evento'), default="P", index=True, copy=False, tracking=True)
    # ultimo_evento = fields.Selection(related='trafico_maritimo_navegacion_id.ultimo_evento', string=_('Evento'), default="P", index=True, copy=False, tracking=True)
    rumbo = fields.Integer(string='Rumbos')
    velocidad = fields.Integer(rstring='Velocidad')
    fecha = fields.Datetime(string='Fecha', default=fields.Datetime.now)