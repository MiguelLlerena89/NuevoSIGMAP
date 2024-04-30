from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class TraficoMaritimoInternacionalCostera(models.Model):
    _name = 'trafico.maritimo.internacional.costera'
    _description = 'Tráfico Marítimo Internacional Costera'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'trafico.maritimo.navegacion': 'trafico_maritimo_navegacion_id'}
    _rec_names_search = ['name','nave_id','ultimo_evento','tipo_trafico','tipo']
    _check_company_auto = True
    _order = 'id desc'

    trafico_maritimo_navegacion_id = fields.Many2one('trafico.maritimo.navegacion', ondelete='restrict', auto_join=True, index=True, store=True,
        string='Tráfico Marítimo Navegación relacionado', help='Información relacionada de tráfico marítimo')

    trafico_maritimo_iaa_id = fields.Many2one('iaa.vessel.voyage.information',
        string='Formulario IAA',
        domain="[('nave_id','=', nave_id),('state','=','aceptado')]"
    )

    fuente_qth = fields.Selection([
        ('nave_propia', 'Nave Propia'),
        ('buque_armada', 'Buque de la Armada'),
        ('avion_capitania', 'Avión de la Capitania'),
        ('costera', 'Costera'),
    ], string=_('Fuente QTH'), index=True, copy=False, tracking=True)

    rumbo = fields.Integer(string='Rumbo')
    velocidad = fields.Integer(string='Velocidad')
    latitud = fields.Float(string='Latitud', digits=(10, 7), readonly=True, store=True)
    longitud = fields.Float(string='Longitud', digits=(10, 7), readonly=True, store=True)
    latitud_dms = fields.Char(string='Latitud DMS', readonly=True, store=True)
    longitud_dms = fields.Char(string='Longitud DMS', readonly=True, store=True)
    fecha_hora_qth = fields.Datetime(string='Fecha - Hora QTH')
    calado_arribo = fields.Float(string="Calado Arribo")

    @api.model
    def create(self, vals):
        code = 'trafico_maritimo_prearribo_code' if vals.get('ultimo_evento') == 'F' else 'trafico_maritimo_prezarpe_code'
        if len(code) ==0:
            raise(('No existe secuencial definido'))
        vals["name"] = self.env["ir.sequence"].next_by_code(code)
        return super().create(vals)

