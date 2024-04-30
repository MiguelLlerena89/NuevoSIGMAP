from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    tiene_matricula = fields.Boolean('Matricula?', compute='_compute_matricula', readonly=True, default=False)

    @api.depends('vat')
    def _compute_matricula(self):
        # Chequear si tiene matrícula? cómo validar matrícula nacional, internacional?
        for rec in self:
            if rec.vat:
                domain = [('matricula','ilike',rec.vat)]
                mat_int = self.env['permar.documento.libretin'].search(domain, limit=1)
                mat_nac = self.env['permar.documento.carnet'].search(domain, limit=1)
                rec.tiene_matricula = bool(mat_int) or bool(mat_nac)
            else:
                rec.tiene_matricula = False

class DocumentoMatriculaBase(models.Model):
    _name = "documento.base.matricula"
    _description = "Documentos Base de Matriculas"
    _inherit = "documento.base"

    tipo_trafico = fields.Many2one(related="personal_maritimo_id.tipo_trafico", store=True)
    es_provisional = fields.Boolean(related="documento_emitido_id.servicio_id.es_provisional", store=True)
    foto_carnet = fields.Image('Foto carnet')
    image_firma = fields.Image('Foto firma')
    jerarquia_id = fields.Many2one(related='documento_emitido_id.tramite_id.jerarquia_id', store=True)
    tipo_sangre = fields.Selection(related='personal_maritimo_id.tipo_sangre', store=True)
    name = fields.Char(string='Nombre')#related='personal_maritimo_id.vat',
    matricula = fields.Char(string='Matrícula', related='personal_maritimo_id.vat', store=True)
    imprimir = fields.Boolean(_('Habilitar impresión?'), default=False)
    reimprimir = fields.Boolean(_('Habilitar reimpresión?'), default=False)
    motivo_reimpresion = fields.Text('Motivo Reimpresión')
    #control_ids = fields.One2many("matricula.control", "carnet_id", string="Control", tracking=True)

    fecha_impresion = fields.Datetime('Fecha Emision', compute='_compute_fecha_emision')

    autorizar = fields.Boolean(_('Confirmar Autorización?'), default=False, compute="_compute_autorizar_impresion")
    state_impresion = fields.Boolean(_('¿Impreso?'), default=False)

    @api.depends("documento_emitido_id.state")
    def _compute_autorizar_impresion(self):
        if self.documento_emitido_id.state in ['vigente']:
            self.autorizar = True
        else:
            self.autorizar = False

    def _default_ficha_medica(self):
        res = []
        domain = [
                    ('company_id', '=', self.company_id.id),
                    ('personal_maritimo_id', '=', self.personal_maritimo_id.id),
                    ('state', '=', 'vigente'),
                ]
        ficha_medica_id = self.env['personal.maritimo.ficha.medica'].search(domain, limit=1)
        if ficha_medica_id:
            res.append({
                'name': ficha_medica_id.name,
                'fecha_caducidad': ficha_medica_id.fecha_caducidad,
            })
        return res

    def validar(self, msg=None):
        msg = msg if msg else ''
        if not self.foto_carnet:
            msg = msg + 'Debe registrar foto de la persona.\n'
        if not self.image_firma:
            msg = msg + 'Debe registrar foto de la firma de la persona.\n'
        if not self.documento_emitido_id:
            msg = msg + 'Debe registrar documento emitido de la persona.\n'
        if not self.tipo_trafico:
            msg = msg + 'Debe definir el tipo de tráfico.\n'
        if not self.tipo_sangre:
            msg = msg + 'Debe definir el tipo de sangre de la persona.\n'
        if self.es_provisional:
            ficha_medica_id = self._default_ficha_medica()
            if not ficha_medica_id:
                msg = msg + 'No tiene ficha médica vigente.\n'
        if msg:
            raise ValidationError(_(msg))

    @api.onchange('state')
    def _onchange_state(self):
        pass

    def button_imprimir_adicional(self):
        self.validar()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["state"] = "en_tramite"
            if 'documento_emitido_id' in vals:
                documento_emitido_id = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
                if documento_emitido_id:
                    vals['jerarquia_id'] = documento_emitido_id.tramite_id.jerarquia_id.id

        return super().create(vals_list)

    def action_documento_matricula_wizard(self, ctx):
        self.ensure_one()
        context = self.env.context
        action = self.env["ir.actions.actions"]._for_xml_id("personal_maritimo_documento.action_documento_matricula_wizard")
        action.update({
            'context': ctx,
            })
        return action

    @api.model
    def validar_como_requerido(self, **kwargs):
        beneficiario = kwargs['personal_maritimo_id']
        model = kwargs['model']
        jerarquia_id = kwargs['jerarquia_id']
        doc = False
        data = [
            ("personal_maritimo_id", "=", beneficiario.id),
            ("jerarquia_id", "=", jerarquia_id.id),
            #("fecha_caducidad", ">=", fecha_tope),
            ("state", "=", 'vigente')
        ]
        doc = self.env[model].search(data, limit=1)
        return doc, bool(doc)
