from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class DocumentoProvisional(models.Model):
    _name = 'permar.documento.provisional'
    _description = 'Permiso Provisional de Embarque / Dispensa Provisional de Jerarquia'
    _inherit = "documento.base"

    tipo = fields.Selection([
            ('permiso_embarque', 'Permiso Provisional de Embarque'),
            ('dispensa', 'Dispensa Provisional de Jeraquia'),
        ],
        string='Tipo Provisional', copy=False, index=True, tracking=True,
    )

    tipo_permiso = fields.Selection([
        ('trabajo', 'Trabajo'),
        ('entrenamiento', 'Entrenamiento'),
    ], 'Tipo Permiso', index=True, copy=False, tracking=True)

    name = fields.Char(string=_("Nombre"), size=100, index=True, tracking=True)
    numero = fields.Char(string=_("Numero"), size=100, index=True, tracking=True)

    nave = fields.Char('Nave a embarcarse', tracking=True)

    personal_maritimo_id = fields.Many2one('personal.maritimo', 'Personal Maritimo', tracking=True)
    jerarquia_id = fields.Many2one(related='personal_maritimo_id.jerarquia_id')

    duracion_dias = fields.Integer('Días')
    fecha_inicio_embarque = fields.Date('Fecha Inicio')
    fecha_fin_embarque = fields.Date('Fecha Fin', compute='_calcular_periodo_caducidad', store=True, tracking=True)

    especialidad_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string='Especialidad Dispensa Provisional', tracking=True)
    observacion = fields.Html('Observaciones')
    documento_provisional_line_ids = fields.One2many('permar.documento.provisional.line', 'documento_povisional_id', string='Lineas de documentos de dispensas', copy=True, tracking=True)

    @api.depends('fecha_inicio_embarque', 'duracion_dias')
    def _calcular_periodo_caducidad(self):
        for rec in self:
            if rec.fecha_inicio_embarque and rec.duracion_dias:
                rec.fecha_fin_embarque = rec.fecha_inicio_embarque + relativedelta(days=+rec.duracion_dias)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals["tipo"] == 'permiso_embarque':
                vals["name"] = self._get_seq_with_company("permiso_provisional_embarque_code") #self.env["ir.sequence"].next_by_code("permiso_provisional_embarque_code")
                #vals["numero"] = self.env["ir.sequence"].next_by_code("permiso_provisional_embarque_code")
            else:
                vals["name"] = self._get_seq_with_company("dispensa_code") #self.env["ir.sequence"].next_by_code("dispensa_code")
            #vals["numero"] = self.env["ir.sequence"].next_by_code("dispensa_code")
            vals["name"] = self._get_seq_with_company("dispensa_code") #self.env["ir.sequence"].next_by_code("dispensa_code")
            vals["state"] = "en_tramite"
            if 'documento_emitido_id' in vals:
                documento_emitido_id = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
                if documento_emitido_id:
                    vals['jerarquia_id'] = documento_emitido_id.tramite_id.jerarquia_id.id
        return super().create(vals_list)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'La documento provisional debe ser único.')
    ]


class DocumentoProvisionalLine(models.Model):
    _name = "permar.documento.provisional.line"
    _description = 'Lineas de documentos permiso de embarque / dispensa'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    documento_povisional_id = fields.Many2one('permar.documento.provisional', string='Permiso Povisional de Embarque / Dispensa')
    fecha_inicio_embarque = fields.Date('Fecha Inicio')
    fecha_fin_embarque = fields.Date('Fecha Fin')
    duracion_dias = fields.Integer('Días')
    personal_maritimo_id = fields.Many2one('personal.maritimo', string="Armador")
    nave = fields.Char('Nave a embarcarse', tracking=True)