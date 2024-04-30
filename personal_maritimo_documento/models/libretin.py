from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = ['personal.maritimo']

    libretin_ids = fields.One2many(
        'permar.documento.libretin', 'personal_maritimo_id', string='Libretín',
        help="Libretín")
    libretin_count = fields.Integer(compute='_compute_libretin_count')

    def _compute_libretin_count(self):
        for partner in self:
            partner.libretin_count = len(partner.libretin_ids)

    def action_open_libretin_enrollment(self):
        self.ensure_one()
        return {
            'name': 'Libretines',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.libretin',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.libretin_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class DocumentoLibretin(models.Model):
    _name = 'permar.documento.libretin'
    _description = 'Matricula Seaman Book'
    _inherit = "documento.base.matricula"

    numero_libretin = fields.Char('Número de Libretín')
    name_previous = fields.Char('Matricula Anterior')
    control_ids = fields.One2many("matricula.control", "libretin_id", string="Control", tracking=True)
    state_impresion_sticker = fields.Boolean(_('¿Sticker Impreso?'))

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
            partner_values['model_id'] = self.env['ir.model'].search([('model','=','permar.documento.libretin')]).id
            partner_values['model_model_id'] = self.id

            self.env['personal.maritimo.foto'].sudo().create(partner_values)
            #self.personal_maritimo_id.sudo().write(partner_values)

    @api.model
    def create(self, vals):
        doc = vals["documento_emitido_id"]
        doc = self.env['tramite.documento.emitido'].search([
            ("id", "=", doc )
            ], limit=1)
        matriculas = self.env['permar.documento.libretin'].search([
            ("personal_maritimo_id", "=", doc.personal_maritimo_id.id ),
            ("state", "=", 'vigente' )
            ])
        for mat in matriculas:
            mat.state = 'caducado'
        vals["name"] = self._get_seq_with_company("documento_libretin_code") #self.env["ir.sequence"].next_by_code("documento_libretin_code")
        self._synchronize_partner_values(vals)
        if doc.tramite_id.tipo_trafico_id.id:
            tipo_trafico_id = doc.tramite_id.tipo_trafico_id.id
            vals['tipo_trafico'] = tipo_trafico_id
        return super().create(vals)

    def write(self, vals):
        self._synchronize_partner_values(vals)
        res = super().write(vals)
        return res

    def button_imprimir(self):
        self.validar()

    def button_reimprimir(self):
        self.validar()
        ctx = dict(
            default_libretin_id = self.id,
        )
        return self.action_documento_matricula_wizard(ctx)

    def button_imprimir_provisional(self):
        self.validar()

    def button_imprimir_adicional(self):
        super().button_imprimir_adicional()
        msg = "Se ha impreso adicional el %s " % (self.documento_emitido_id.name_get()[0][1])
        self.message_post(body=msg)
        return self.env.ref('personal_maritimo_documento.action_report_documento_libretin_adicional').report_action(self)

    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'permar.documento.libretin')
                ]
            print(domain)
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.libretin',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)
                print('follower_id')
                print(follower_id)

    def validar(self):
        msg = ''
        msg = msg + 'No puede generar un libretín para tráfico nacional.\n' if self.tipo_trafico.tipo == 'NAC' else ''
        msg = msg + 'Debe ingresar el número de libretín.\n' if not self.numero_libretin else ''
        super().validar(msg)

    # def write(self, vals):
    #     self._synchronize_partner_values(vals)
    #     res = super().write(vals)
    #     #self._add_followers()
    #     return res

    def action_previsualizar_libretin(self):
        self.ensure_one()
        msg = "Se ha visualizado previamente el libretín del expediente: %s " % (self.documento_emitido_id.name_get()[0][1])
        self.message_post(body=msg)
        action_report_id = self.env.ref('personal_maritimo_documento.action_report_documento_previo_libretin')
        action_report_id.report_type = 'qweb-html'
        result = action_report_id.report_action(self.id)
        return result
        #return self.env.ref('personal_maritimo_documento.action_report_documento_libretin').report_action(self)

    def action_imprimir_libretin(self):
        self.state_impresion = True
        msg = "Se ha impreso libretín del expediente: %s " % (self.documento_emitido_id.name_get()[0][1])
        self.message_post(body=msg)
        return self.env.ref('personal_maritimo_documento.action_report_documento_libretin').report_action(self)

    def action_imprimir_curso_libretin(self):
        self.state_impresion_sticker = True
        msg = "Se ha impreso sticker de curso de libretín del expediente: %s " % (self.documento_emitido_id.name_get()[0][1])
        self.message_post(body=msg)
        return self.env.ref('personal_maritimo_documento.action_report_documento_curso_libretin').report_action(self)


class MatriculaControl(models.Model):
    _inherit = "matricula.control"

    libretin_id = fields.Many2one("permar.documento.libretin", string="Matrícula Seaman Book", tracking=True)

class MatriculaControlSuministro(models.Model):
    _inherit = "matricula.control.suministro"

    libretin_id = fields.Many2one(related="control_id.libretin_id", tracking=True)