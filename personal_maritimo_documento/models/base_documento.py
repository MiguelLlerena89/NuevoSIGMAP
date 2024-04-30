from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class DocumentoBase(models.AbstractModel):
    _name = "documento.base"
    _description = "Documento base"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _inherits = {'tramite.documento.emitido': 'documento_emitido_id'}

    READONLY_STATES = { state: [('readonly', True)] for state in {'vigente', 'caducado', 'anulado', 'cancelado'}}

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
    name = fields.Char(string=_("Nombre"), size=100, index=True, states=READONLY_STATES, tracking=True)
    numero = fields.Char(string=_("Numero"), size=100, index=True, states=READONLY_STATES, tracking=True)

    numero_formato = fields.Integer(string="Número de Formato", tracking=True)

    active = fields.Boolean(string=_('Activo?'), default=True) #states=READONLY_STATES

    def _get_seq_with_company(self, code):
        return self.env.user.company_id.name + '-' + self.env["ir.sequence"].next_by_code(code)

    def _get_persona_autoridad_firma(self):
        res = []
        persona_autoridad_actual_id = self.env['persona.autoridad'].search([('company_id', '=', self.env.company.id), ('active','=', True)], limit=1)
        if persona_autoridad_actual_id:
            res.append({
                'texto_firma': persona_autoridad_actual_id.texto_firma,
                'rango_name': persona_autoridad_actual_id.rango_id.name,
                'texto_cargo': persona_autoridad_actual_id.texto_cargo,
                'image_firma': persona_autoridad_actual_id.image_firma,
            })
        return res

    def _get_sumillas(self):
        result = ''
        res = []
        ref_sumilla = []
        if self.message_follower_ids:
            for i in self.message_follower_ids:
                user_id = self.env['res.users'].search([('partner_id', '=', i.partner_id.id)])
                sumilla_usuario_id = self.env['sumilla.usuario'].search([('sumilla_user_id', '=', user_id.id)])
                if sumilla_usuario_id:
                    ref_sumilla.append(sumilla_usuario_id.sumilla)
            if len(ref_sumilla) > 0:
                result = '/'.join((ref_sumilla))
        res.append({'sumilla': result})
        return res

    def action_nuevo_formato_wizard(self, ctx):
        self.ensure_one()
        context = self.env.context
        action = self.env["ir.actions.actions"]._for_xml_id("personal_maritimo_documento.action_documento_numero_formato_wizard")
        action.update({
            'context': ctx,
            })
        return action

    def write(self, vals):
        res = super().write(vals)
        # self._add_followers()
        return res

    @api.model
    def create(self, vals):
        if 'documento_emitido_id' in vals:
            doc = self.env["tramite.documento.emitido"].search([
                    ("id", "=", vals["documento_emitido_id"]),
                    ], limit=1)
            model = doc.model_model
            if model not in ['permar.documento.carnet', 'permar.documento.libretin']:
                today = fields.Date.context_today(self)
                if not doc.fecha_caducidad:
                    raise ValidationError('Debe definir la fecha de caducidad')
                #vals["state"] = "vigente" if doc.fecha_caducidad > today else "caducado"
        return super().create(vals)

    @api.model
    def validar_requisito(self, beneficiario, tramite, model, line):
        doc = False
        data = [
            ("personal_maritimo_id", "=", beneficiario.id),
        ]
        doc = self.env[model].search(data, limit=1)
        return doc

    def _get_imagen_fondo_documento(self):
        return self.env['ir.config_parameter'].sudo().get_param('base_sigmap.imagen_fondo_documento')

    def validar(self):
        if self.personal_maritimo_id and self.personal_maritimo_id.partner_id.company_type == 'person':
            self.personal_maritimo_id.validar_permar()

    def action_generar_documento(self):
        self.validar()
        self.documento_emitido_id.action_generar_documento()

    @api.model
    def validar_como_requerido(self, **kwargs):
        beneficiario = kwargs['personal_maritimo_id']
        model = self._name
        doc = False
        params = self.env['ir.config_parameter'].sudo()
        tiempo_minimo_validez_documentos = params.get_param("tramite.tiempo_minimo_validez_documentos")
        fecha_tope = date.today() + relativedelta(months=int(tiempo_minimo_validez_documentos))
        data = [
            ("personal_maritimo_id", "=", beneficiario.id),
            ("fecha_caducidad", ">=", fecha_tope),
            ("state", "=", 'vigente')
        ]
        doc = self.env[model].search(data, limit=1)
        return doc, bool(doc)
