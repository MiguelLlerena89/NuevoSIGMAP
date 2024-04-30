
import base64
import json

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class NaveDocumentoBase(models.AbstractModel):
    _name = "nave.documento.base"
    _description = "Documento Base de Nave"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _inherits = {'tramite.documento.emitido': 'documento_emitido_id'}

    READONLY_STATES = { state: [('readonly', True)] for state in {'vigente', 'caducado', 'anulado'}}

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Usuario', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    documento_emitido_id = fields.Many2one(
        "tramite.documento.emitido",
        string=_("Documento emitido"),
        ondelete='cascade',
        states=READONLY_STATES,
        tracking=True)
    partner_id = fields.Many2one(
        related='documento_emitido_id.tramite_id.order_id.partner_id',
        string=_('Solicitante'),
        store=True,
        index=True,
        copy=False,
        tracking=True,
        states=READONLY_STATES)

    reparto_id = fields.Many2one(
        related='documento_emitido_id.tramite_id.nave_id.reparto_id',
        string=_('Reparto'),
        store=True,
        index=True,
        copy=False,
        tracking=True,
        states=READONLY_STATES)

    nave_inspeccion_id = fields.Many2one(related="documento_emitido_id.tramite_id.nave_inspeccion_id", string=_("Inspección"), tracking=True)
    calificacion_final = fields.Selection(related="documento_emitido_id.tramite_id.nave_inspeccion_id.calificacion_final", string=_('Calificación'), tracking=True)

    name = fields.Char(string=_("Nombre"), size=100, index=True, states=READONLY_STATES, tracking=True)
    numero = fields.Char(string=_("Numero"), size=100, index=True, states=READONLY_STATES, tracking=True)

    numero_formato = fields.Integer(string="Número de Formato", tracking=True)
    observacion = fields.Html('Observaciones')

    active = fields.Boolean(string=_('Activo?'), default=True)

    es_oficio = fields.Boolean('Es Oficio?', readonly=True, index=True, copy=False, tracking=True)

    attachments_required = fields.Boolean(
        related='documento_emitido_id.tramite_id.servicio_id.attachments_required', states=READONLY_STATES, store=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    def _get_seq_with_company(self, code):
        return '%s-%s' % (self.env.user.company_id.name, self.env["ir.sequence"].next_by_code(code))

    def _get_seq_with_reparto(self, siglas, code):
        return '%s-%s' % (siglas, self.env["ir.sequence"].next_by_code(code))

    def validar(self):
        pass

    def write(self, vals):
        res = super().write(vals)
        return res

    def _prepare_file_name(self):
        return self.documento_emitido_id._prepare_file_name()

    def action_generar_documento(self):
        self.validar()
        self.documento_emitido_id.action_generar_documento()

    @api.model
    def validar_como_requerido(self, **kwargs):
        # Busca documento emitido vigente (nave)
        model = kwargs['model']
        nave_id = kwargs['nave_id']
        dom = [
            ('state', '!=', 'utilizado'),
            ('nave_id', '=', nave_id.id),
        ]

        record = self.env[model].search(dom, limit=1, order='create_date desc')
        es_completado = record and (record.state == 'vigente')
        return record, es_completado
