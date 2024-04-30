from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class Tramite(models.Model):
    _inherit = "tramite"

    ultimo_evento = fields.Selection(related="servicio_id.ultimo_evento")
    tipo_trafico_id = fields.Many2one(related='nave_id.tipo_trafico_id', string=_('Tipo Tráfico'), readonly=True, store=True, tracking=True)
    tipo = fields.Selection(related='tipo_trafico_id.tipo', string=_('Tipo'), readonly=True, store=True, tracking=True)
    trb = fields.Float(related='nave_id.trb', string=_('TRB'), readonly=True, store=True, tracking=True)
    estado_navegacion = fields.Selection(related='nave_id.estado_navegacion', string=_('Estado de Navegación'), readonly=True, store=True, tracking=True)

    reparto_id = fields.Many2one(related='nave_id.reparto_id', string=_("Reparto Nave"), store=True, tracking=True, readonly=True)
    reparto_origen_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Juridicción'),
        store=True,
        index=True,
        copy=False,
        tracking=True)
    reparto_final_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Juridicción'),
        store=True,
        index=True,
        copy=False,
        tracking=True)

    fecha_origen = fields.Datetime(string="Fecha", default=fields.Datetime.now)
    fecha_destino = fields.Datetime(string="Fecha", default=fields.Datetime.now)
    # periodo_navegacion = fields.Char(string="Período de Navegación", compute="_calcular_periodo_navegacion")
    # dias_tiempo_espera = fields.Integer('Días de tiempo de espera', compute="_calcular_periodo_navegacion")

    servicio_id = fields.Many2one("tramite.documento",
        domain = "[('tipo_documento_id', '=', tipo_documento_id)]",
        string=_("Servicio"), required=True, tracking=True)

    trafico_maritimo_prenavegacion_id = fields.Many2one("trafico.maritimo.internacional.costera",
        string=_("Tráfico Marítimo Pre Navegación"), index=True, tracking=True)

    def _get_ultimo_movimiento_navegacion(self, nave, tipo):
        domain = [
            ('nave_id','=', nave.id),
            ('tipo','=', nave.tipo_trafico_id.tipo),
        ]
        navegacion = self.env['trafico.maritimo.navegacion'].search(domain, order='id desc', limit=1)
        if navegacion:
            proxima_navegacion,_ = navegacion._get_evento_inverso_navegacion(navegacion.ultimo_evento)
        else:
            proxima_navegacion = 'Z'
        return proxima_navegacion

    @api.onchange("servicio_id")
    def _onchange_servicio_id(self):
        #self.order_id._check_trafico_maritimo_nave()
        documento_ids = False
        tipo_documento_id = self.order_id.tipo_documento_id.id
        domain = [('tipo_documento_id','=', tipo_documento_id)]
        trafico_maritimo_id = self.env.ref("base_sigmap.trafico_maritimo").id
        if tipo_documento_id == trafico_maritimo_id:
            nave = self.order_id.nave_id
            if nave:
                tipo = nave.tipo_trafico_id.tipo
                domain.append(('tipo','=', nave.tipo_trafico_id.tipo))
                if tipo == 'NAC':
                    if self.nave_id.estado_navegacion == 'en puerto' or self.servicio_id.id in [self.env.ref("tramite.tramite_documento_218").id, self.env.ref("tramite.tramite_documento_219").id, self.env.ref("tramite.tramite_documento_222").id]:
                        self.reparto_origen_id = self.nave_id.reparto_id.id
                    proxima_navegacion = self._get_ultimo_movimiento_navegacion(nave, tipo)
                    domain.append(('ultimo_evento','=',proxima_navegacion))
                else:
                    domain_trafico_maritimo_nave = [
                        ('nave_id','=', nave.id),
                        ('tramite_id', '=', False),
                    ]
                    trafico_internacional_id = self.env["trafico.maritimo.internacional.costera"].search(domain_trafico_maritimo_nave, limit=1)
                    if trafico_internacional_id.ultimo_evento == 'P':
                        domain.append(('ultimo_evento','=','Z'))
                        self.nave_id.estado_navegacion = 'prezarpe'
                    else:
                        domain.append(('ultimo_evento','=','A'))
                        self.nave_id.estado_navegacion = 'prearribo'
                    self.trafico_maritimo_prenavegacion_id = trafico_internacional_id.id
                    self.reparto_origen_id = trafico_internacional_id.reparto_origen_id if trafico_internacional_id.reparto_origen_id else False
                    self.reparto_final_id = trafico_internacional_id.reparto_final_id
                    self.fecha_origen = trafico_internacional_id.fecha_origen if trafico_internacional_id.fecha_origen else False
                    self.fecha_destino = trafico_internacional_id.fecha_destino
            else:
                domain = [('id','=', 0)]
            #     raise ValidationError(_("Debe seleccionar una nave"))
        documento_ids = self.env['tramite.documento'].search(domain).ids
        return {'domain': {'servicio_id': [('id', 'in', documento_ids)]}}

    @api.onchange("reparto_origen_id")
    def _onchange_reparto_origen_id(self):
        domain = []
        if self.nave_id and self.nave_id.tipo == 'NAC':
            if self.nave_id.estado_navegacion == 'en puerto' or self.servicio_id.id in [self.env.ref("tramite.tramite_documento_218").id, self.env.ref("tramite.tramite_documento_219").id, self.env.ref("tramite.tramite_documento_222").id]:
                nave_creada = self.nave_id.reparto_id
                domain.append(nave_creada.id)
                nave_contruida = self.env['nave.nave.construccion'].search([('nave_id','=', self.nave_id.id)], order='id desc', limit=1)
                if nave_contruida:
                    if nave_creada.id != nave_contruida.reparto_id.id:
                        domain.append(nave_contruida.reparto_id.id)
        print(domain)
        return {'domain': {'reparto_origen_id': [('id', 'in', domain)]}}

    # @api.depends('fecha_origen', 'fecha_destino')
    # def _calcular_periodo_navegacion(self):
    #     for rec in self:
    #         if rec.fecha_origen and rec.fecha_destino:
    #             periodo = ''
    #             diff = rec.fecha_destino - rec.fecha_origen
    #             dias = diff.days #relativedelta(rec.fecha_destino, rec.fecha_origen).days
    #             horas = relativedelta(rec.fecha_destino,rec.fecha_origen).hours #diff.seconds / 3600 #relativedelta(rec.fecha_destino, rec.fecha_origen).hours
    #             if diff.days:
    #                 periodo+= str(dias) + ' días '
    #             if horas:
    #                 periodo+= str(horas) + ' horas '
    #             rec.dias_tiempo_espera = int(dias)
    #             rec.periodo_navegacion = periodo

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            print(vals)
        res = super().create(vals_list)
        res.trafico_maritimo_prenavegacion_id.sudo().write({'tramite_id': res.id})