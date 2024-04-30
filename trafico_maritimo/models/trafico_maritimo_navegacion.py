from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class TraficoMaritimoNavegacion(models.Model):
    _name = 'trafico.maritimo.navegacion'
    _description = 'Tráfico Marítimo Navegacion'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    #READONLY_STATES = { state: [('readonly', True)] for state in {'vigente', 'caducado', 'anulado', 'cancelado'}}
    name = fields.Char(string=_("Nombre"), store=True, readonly=True, index=True, tracking=True)
    company_id = fields.Many2one('res.company', string=_('Company'), required=True, index=True, default=lambda self: self.env.company.id)
    user_id = fields.Many2one(
        'res.users', string=_('User'), index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)

    #1. BUQUE
    nave_id = fields.Many2one('nave.nave', string=_('Buque'), domain="[('tipo', '=', tipo)]", required=True, index=True, copy=False, tracking=True)
    call_sign = fields.Char(string=_("Call Sign"),
        related='nave_id.senial_llamada',
        readonly=True,
        index=True,
        copy=False,
        help="IMO0136",
        tracking=True)

    omi_number = fields.Char(string=_('OMI Number'),
        related='nave_id.omi_number',
        index=True,
        copy=False,
        help="IMO0140",
        tracking=True)

    matricula = fields.Char(string=_('Matrícula'),
        related='nave_id.matricula',
        index=True,
        copy=False,
        tracking=True)

    nave_tipo_id = fields.Many2one(
        related='nave_id.nave_tipo_id',
        readonly=True,
        string=_('Tipo Nave'),
        index=True,
        copy=False,
        tracking=True)

    nave_servicio_id = fields.Many2one(
        related='nave_id.nave_servicio_id',
        readonly=True,
        string=_('Tipo Servicio'),
        index=True,
        copy=False,
        tracking=True)

    eslora = fields.Float(
        related='nave_id.eslora',
        string=_('Eslora'),
        readonly=True,
        index=True,
        copy=False,
        tracking=True)

    manga = fields.Float(
        related='nave_id.manga',
        string=_('Manga'),
        readonly=True,
        index=True,
        copy=False)

    puntal = fields.Float(
        related='nave_id.puntal',
        string=_('Puntal'),
        readonly=True,
        index=True,
        copy=False)

    trb = fields.Float(string=_('TRB'),
        related='nave_id.trb',
        readonly=True,
        index=True,
        copy=False,
        tracking=True)

    trn = fields.Float(string=_('TRN'),
        related='nave_id.trn',
        readonly=True,
        index=True,
        copy=False,
        tracking=True)

    mmsi = fields.Char(string='MMSI',
        related='nave_id.mmsi',
        readonly=True,
        index=True,
        copy=False,
        tracking=True
    )

    lista_autorizada = fields.Selection(
        related='nave_id.lista_autorizada',
        string='Lista Autorizada',
        readonly=True,
        index=True,
        copy=False,
        tracking=True)

    bandera_pais_id = fields.Many2one(related='nave_id.bandera_pais_id', string=_('Bandera'), readonly=True, tracking=True)
    nave_nationality = fields.Char(related='bandera_pais_id.nationality', string=_('Nationality'), readonly=True, tracking=True)

    shipping_line_id = fields.Many2one('res.partner', string=_('Shipping Line'))
    employee_shipping_line_id = fields.Many2one('res.partner', string=_('Shipping agency employee'))
    shipowner_id = fields.Many2one('res.partner', string=_('Shipowner'))

    calado = fields.Float(string='Calado')
    proa = fields.Float(string='Proa')
    popa = fields.Float(string='Popa')
    velocidad = fields.Integer(string='Velocidad')
    # carga_exportacion_del_puerto = fields.Boolean(string='Carga de exportacion del Puerto')
    # carga_transito = fields.Boolean(string='Carga en Tránsito')

    ultimo_evento = fields.Selection([
        ('A', 'Arribo'),
        ('Z', 'Zarpe'),
        ('S', 'Salío de Área Sitrame'),
        ('P', 'Plan de viaje (previo arribo/zarpe)'),
        ('F', 'Prearribo'),
        ('QTH', 'Qth'),
    ], string=_('Último Evento'), store=True, required=True, index=True, copy=False, tracking=True)
    ultimo_evento_descripcion = fields.Char('Descripción del Evento', compute='_compute_ultimo_evento_descripcion')

    tipo = fields.Selection([
            ('INT', 'INTERNACIONAL'),
            ('NAC', 'NACIONAL'),
        ],
        string='Tipo', copy=False, index=True, tracking=True,
    )
    tipo_trafico_id = fields.Many2one('tipo.trafico', string='Tipo Tráfico', domain="[('tipo','=',tipo)]", index=True, copy=False, tracking=True)
    #tipo = fields.Selection(related='tipo_trafico_id.tipo', string=_('Tipo'), readonly=True, store=True, tracking=True)

    #Navegacion
    reparto_origen_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Juridicción'),
        #required=True,
        #store=True,
        index=True,
        copy=False,
        help='IMO0112',
        tracking=True)

    reparto_final_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Juridicción'),
        #required=True,
        index=True,
        copy=False,
        help='IMO0112',
        tracking=True)

    puerto_origen_id = fields.Many2one(
        'sigmap.puerto',
        string=_('Puerto Origen'),
        domain = "[('reparto_id','=',reparto_origen_id)]",
        index=True,
        copy=False,
        tracking=True)

    puerto_destino_id = fields.Many2one(
        'sigmap.puerto',
        string=_('Puerto Destino'),
        domain = "[('reparto_id','=',reparto_final_id)]",
        index=True,
        copy=False,
        tracking=True)

    fecha_despacho = fields.Datetime(string="Fecha de Despacho o Emisión", default=fields.Datetime.now)
    fecha_origen = fields.Datetime(string="Fecha") #, default=fields.Datetime.now
    fecha_destino = fields.Datetime(string="Fecha") #, default=fields.Datetime.now

    puntal_calado_aereo = fields.Char(compute='_compute_puntal_calado_aereo')

    observacion = fields.Html('Observaciones')
    active = fields.Boolean(string=_('Active?'), default=True)

    @api.depends('ultimo_evento')
    def _compute_ultimo_evento_descripcion(self):
        eventos = dict(self._fields['ultimo_evento']._description_selection(self.env))
        for rec in self:
            rec.ultimo_evento_descripcion = eventos[rec.ultimo_evento]

    @api.depends('nave_id')
    def _compute_puntal_calado_aereo(self):
        self.puntal_calado_aereo = '%s/%s/%s' % (self.nave_id.puntal, self.nave_id.calado, self.nave_id.calado_aereo)

    def validate_zarpe(self):
        print('reparto.......................')
        print(self.reparto_origen_id)
        msg = ''
        if not self.reparto_origen_id:
            msg = msg + 'Debe seleccionar el Reparto.\n'
        else:
            if not self.reparto_origen_id.siglas:
                msg = msg + 'Debe definir las siglas del Reparto.\n'
        if msg:
            raise ValidationError(_(msg))
        return True

    @api.model
    def _get_evento_inverso_navegacion(self, evento):
        reverse = ''
        model = ''
        if evento == 'Z':
            reverse = 'A'
            model = 'trafico.maritimo.arribo'
        elif evento == 'A':
            reverse = 'Z'
            model = 'trafico.maritimo.zarpe'
        else:
            raise ValidationError(_('No existe ese tipo de evento de navegación.'))
        return reverse, model