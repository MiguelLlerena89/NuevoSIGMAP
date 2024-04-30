from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    dispensa_ids = fields.One2many(
        'permar.documento.dispensa', 'personal_maritimo_id', string="Dispensa")
    dispensa_count = fields.Integer(compute='_compute_dispensa_count')

    def _compute_dispensa_count(self):
        for partner in self:
            partner.dispensa_count = len(partner.dispensa_ids.filtered(lambda c: c.company_id == self.env.company))

    def action_open_dispensa_enrollment(self):
        self.ensure_one()
        return {
            'name': 'Dispensa',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.dispensa',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.dispensa_ids.filtered(lambda c: c.company_id == self.env.company).ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }

class Dispensa(models.Model):
    _name = 'permar.documento.dispensa'
    _description = 'Dispensa'
    _inherit = "documento.base"

    jerarquia_cargo_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string='Jerarquía a desempeñar', store=True)
    nave_id = fields.Many2one('nave.nave', 'Nave', tracking=True)
    jerarquia_id = fields.Many2one(related='personal_maritimo_id.jerarquia_id')

    duracion_dias = fields.Integer('Días', default=0, compute="_calcular_dias_duracion", store=True, readonly=False, tracking=True)

    fecha_inicio_embarque = fields.Date('Fecha Inicio')
    fecha_fin_embarque = fields.Date('Fecha Fin', compute='_calcular_periodo_caducidad', store=True, tracking=True)

    observacion = fields.Html('Observaciones')
    dispensa_line_ids = fields.One2many('permar.documento.dispensa', compute="_compute_dispensa_anteriores", string='Lineas de documentos de dispensas', copy=True, tracking=True)

    @api.depends('jerarquia_id')
    def _compute_dispensa_anteriores(self):
        for permiso in self:
            active = permiso.personal_maritimo_id.jerarquia_ids.filtered(lambda c: c.active)

            fecha_inicio_jerarquia = active.fecha_ingreso

            domain = [
                ('id', '!=', permiso.id),
                ('personal_maritimo_id', '=', permiso.personal_maritimo_id.id),
                ('jerarquia_id', '=', permiso.jerarquia_id.id),
                ('fecha_inicio_embarque', '>=', fecha_inicio_jerarquia),
                ('fecha_fin_embarque', '<=', permiso.fecha_fin_embarque )
            ]
            permiso.dispensa_line_ids = self.env['permar.documento.dispensa'].search(domain)

    @api.depends('fecha_inicio_embarque', 'fecha_fin_embarque')
    def _calcular_dias_duracion(self):
        # Calcular días duración a partir del rango de fechas
        for rec in self:
            if rec.fecha_inicio_embarque and rec.fecha_fin_embarque:
                duracion = rec.fecha_fin_embarque - rec.fecha_inicio_embarque
                rec.duracion_dias = duracion.days

    @api.depends('fecha_inicio_embarque', 'duracion_dias')
    def _calcular_periodo_caducidad(self):
        # Calcular fecha fin de embarque a partir de los días ingresados
        for rec in self:
            if rec.fecha_inicio_embarque and rec.duracion_dias:
                rec.fecha_fin_embarque = rec.fecha_inicio_embarque + relativedelta(days=+rec.duracion_dias)

    def action_validar(self):
        #self._validate_ficha_medica()
        if self.duracion_dias:
            # Actualizar los días de permiso en la jerarquía activa
            actives = self.personal_maritimo_id.jerarquia_ids.filtered(lambda c: c.active)
            # Verificar que sea una

            if actives.dias_disponibles_dispensa > self.duracion_dias:
                print(self.duracion_dias)
                dias_disponibles = actives.dias_disponibles_dispensa
                print(dias_disponibles)
                actives.dias_disponibles_dispensa = dias_disponibles - self.duracion_dias
                print(actives.dias_disponibles_dispensa)
            else:
                raise ValidationError('Los días que tiene disponibles son menores a los días de permiso ingresados.')

    @api.depends('duracion_dias')
    def validate_duracion_dias(self):
        if self.duracion_dias and self.duracion_dias <= 0 or self.duracion_dias > 180:
            raise ValidationError('Número de días provisional inválido.')

    #@api.onchange('duracion_dias')
    @api.constrains('duracion_dias')
    def _check_duracion_dias(self):
        self.validate_duracion_dias()

    # def action_print_dispensa(self):
    #     return self.env.ref('personal_maritimo_documento.action_report_dispensa').report_action(self)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self._get_seq_with_company("dispensa_code") #self.env["ir.sequence"].next_by_code("dispensa_code")
            vals["state"] = "en_tramite"
            if 'documento_emitido_id' in vals:
                documento_emitido_id = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
                if documento_emitido_id:
                    vals['jerarquia_id'] = documento_emitido_id.tramite_id.jerarquia_id.id
        return super().create(vals_list)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'La dispensa debe ser único.')
    ]


class DispensaLine(models.Model):
    _name = "permar.documento.dispensa.line"
    _description = 'Lineas de documentos de dispensas'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    dispensa_id = fields.Many2one('permar.documento.dispensa', string='Dispensa')
    fecha_inicio_embarque = fields.Date('Fecha Inicio')
    fecha_fin_embarque = fields.Date('Fecha Fin')
    duracion_dias = fields.Integer('Días')
    personal_maritimo_id = fields.Many2one('personal.maritimo', string="Armador")
    nave_id = fields.Many2one('nave.nave', 'Nave', tracking=True)
