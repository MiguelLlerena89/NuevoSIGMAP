from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = ['personal.maritimo']

    carnet_ids = fields.One2many(
        'permar.documento.carnet', 'personal_maritimo_id', string='Carnet Marítimo',
        help="Carnet")
    carnet_count = fields.Integer(compute='_compute_carnet_count')

    def _compute_carnet_count(self):
        for partner in self:
            partner.carnet_count = len(partner.carnet_ids)

    def action_open_carnet_enrollment(self):
        self.ensure_one()
        return {
            'name': 'Carnets',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.carnet',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.carnet_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class DocumentoCarnet(models.Model):
    _name = 'permar.documento.carnet'
    _description = 'Documento Carnet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherit = "documento.base.matricula"

    control_ids = fields.One2many("matricula.control", "carnet_id", string="Control", tracking=True)

    @api.depends('control_ids')
    def _compute_fecha_emision(self):
        self.fecha_impresion = self.control_ids.search([], limit=1, order='fecha_impresion asc').fecha_impresion

    def _synchronize_partner_values(self, vals):
        partner_values = {}
        if 'foto_carnet' in vals:
            partner_values['image_foto'] = vals['foto_carnet']
        if 'image_firma' in vals:
            partner_values['image_firma'] = vals['image_firma']
        if partner_values:
            partner_values['company_id'] = self.company_id.id
            partner_values['personal_maritimo_id'] = self.personal_maritimo_id.id
            partner_values['user_id'] = self.user_id.id
            partner_values['fecha_inicio'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            partner_values['model_id'] = self.env['ir.model'].search([('model','=','permar.documento.carnet')]).id
            partner_values['model_model_id'] = self.id

            self.env['personal.maritimo.foto'].sudo().create(partner_values)
            #self.personal_maritimo_id.sudo().write(partner_values)

    @api.model
    def create(self, vals):
        doc = vals["documento_emitido_id"]
        doc = self.env['tramite.documento.emitido'].search([
            ("id", "=", doc )
            ], limit=1)
        carnets = self.env['permar.documento.carnet'].search([
            ("personal_maritimo_id", "=", doc.personal_maritimo_id.id ),
            ("state", "=", 'vigente' )
            ])
        for carnet in carnets:
            carnet.state = 'caducado'

        vals["name"] = self._get_seq_with_company("documento_carnet_code") #self.env["ir.sequence"].next_by_code("documento_carnet_code")
        self._synchronize_partner_values(vals)
        return super().create(vals)

    def write(self, vals):
        # vals['model'] = 'permar.documento.carnet'
        # vals['id'] = self.id
        self._synchronize_partner_values(vals)
        return super().write(vals)

    def _get_imagen_fondo_matricula(self):
        return self.env['ir.config_parameter'].sudo().get_param('personal_maritimo.imagen_fondo_matricula')

    def validar(self):
        msg = ''
        msg = msg + 'No está configurada la imagen de fondo de matrícula.\n' if not self._get_imagen_fondo_matricula() else ''
        msg = msg + 'No puede generar un carnet para tráfico internacional.\n' if self.tipo_trafico.tipo == 'INT' else ''
        super().validar(msg)

    def action_generar_documento(self):
        self.validar()
        for carnet in self:
            carnet.write({
                "state": "vigente",
                "control_ids": [(0, 0, {
                    "name": "Impresión carnet",
                    }
                )]
            })
        msg = "Se ha impreso el %s " % (self.documento_emitido_id.name_get()[0][1])
        self.message_post(body=msg)
        super().action_generar_documento()

    def button_reimprimir(self):
        self.validar()
        ctx = dict(
            default_carnet_id = self.id,
        )
        return self.action_documento_matricula_wizard(ctx)

    def button_imprimir_provisional(self):
        self.validar()

    def button_imprimir_adicional(self):
        super().button_imprimir_adicional()
        msg = "Se ha impreso adicional el %s " % (self.documento_emitido_id.name_get()[0][1])
        self.message_post(body=msg)
        return self.env.ref('personal_maritimo_documento.action_report_documento_carnet_adicional').report_action(self)

    def disable_autorizar(self):
        if self.es_provisional:
            self.autorizar = False

    def action_autorizar(self):
        self.imprimir = True

    # def action_anular(self):
    #     if not self.es_provisional:
    #         self.autorizar = False
    #     self.imprimir = False
    #     super().action_anular()

    @api.onchange('es_provisional')
    def onchange_es_provisional(self):
        if self.es_provisional:
            self.autorizar = False

    def action_imprimir_carnet(self):
        self.state_impresion = True
        msg = "Se ha impreso carnet del expediente: %s " % (self.documento_emitido_id.name_get()[0][1])
        self.message_post(body=msg)
        return self.env.ref('personal_maritimo_documento.action_report_documento_carnet').report_action(self)

class DocumentoControl(models.Model):
    _inherit = "matricula.control"

    carnet_id = fields.Many2one("permar.documento.carnet", string="Carnet", tracking=True)

class DocumentoControlSuministro(models.Model):
    _inherit = "matricula.control.suministro"

    carnet_id = fields.Many2one(related="control_id.carnet_id", tracking=True)