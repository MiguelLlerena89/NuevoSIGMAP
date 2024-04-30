from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    permiso_provisional_ids = fields.One2many(
        'permar.documento.permiso.provisional.embarque', 'personal_maritimo_id', string='Permiso provisional')
    permiso_provisional_count = fields.Integer(compute='_compute_permiso_provisional_count')

    def _compute_permiso_provisional_count(self):
        for partner in self:
            partner.permiso_provisional_count = len(partner.permiso_provisional_ids.filtered(lambda c: c.company_id == self.env.company))

    def action_open_permiso_provisional_enrollment(self):
        self.ensure_one()
        return {
            'name': 'Permiso Provisional de Embarque',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.permiso.provisional.embarque',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.permiso_provisional_ids.filtered(lambda c: c.company_id == self.env.company).ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }

class PermisoProvisionalEmbarque(models.Model):
    _name = 'permar.documento.permiso.provisional.embarque'
    _description = 'Permiso Provisional de Embarque'
    _inherit = "documento.base"

    #especialidad = fields.Char(string=_("Especialidad"), size=100, index=True, tracking=True)
    name = fields.Char(string=_("Nombre"), size=100, index=True, tracking=True)
    numero = fields.Char(string=_("Numero"), size=100, index=True, tracking=True)

    nave_id = fields.Many2one('nave.nave', 'Nave', tracking=True)
    armador_id = fields.Many2one('sigmap.armador', 'Armador', tracking=True)
    jerarquia_id = fields.Many2one(related='personal_maritimo_id.jerarquia_id', store=True)
    jerarquia_cargo_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string='Jerarquía a desempeñar', store=True)

    duracion_dias = fields.Integer('Días', default=0, compute="_calcular_dias_duracion", store=True, readonly=False, tracking=True)

    fecha_inicio_embarque = fields.Date('Fecha Inicio')
    fecha_fin_embarque = fields.Date('Fecha Fin', compute='_calcular_periodo_caducidad', store=True, readonly=False, tracking=True)

    tipo_permiso_id = fields.Many2one('permar.permiso.provisional.embarque.tipo', string='Tipo permiso provisional', tracking=True)

    observacion = fields.Html('Observaciones')
    #carnet_id = fields.Many2one('permar.documento.carnet', string='No. Carnet', domain=[('tipo','=','NAC')], index=True, copy=False, tracking=True)
    carnet_id = fields.Many2one('permar.documento.carnet', string='No. Carnet', index=True, copy=False, tracking=True)

    permiso_provisional_embarque_line_ids = fields.One2many('permar.documento.permiso.provisional.embarque', compute="_compute_permisos_anteriores", string='Lineas de Permisos Provisionales de Embarque', copy=True, tracking=True)

    @api.depends('jerarquia_id')
    def _compute_permisos_anteriores(self):
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
            permiso.permiso_provisional_embarque_line_ids = self.env['permar.documento.permiso.provisional.embarque'].search(domain)


    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'permar.documento.permiso.provisional.embarque')
                ]
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.permiso.provisional.embarque',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)

    def action_validar(self):
        #self._validate_ficha_medica()
        if self.duracion_dias:
            # Actualizar los días de permiso en la jerarquía activa
            actives = self.personal_maritimo_id.jerarquia_ids.filtered(lambda c: c.active)
            # Verificar que sea una

            if actives.dias_disponibles_provisional > self.duracion_dias:
                dias_disponibles = actives.dias_disponibles_provisional
                actives.dias_disponibles_provisional = dias_disponibles - self.duracion_dias
            else:
                raise ValidationError('Los días que tiene disponibles son menores a los días de permiso ingresados.')

    @api.depends('fecha_inicio_embarque', 'fecha_fin_embarque')
    def _calcular_dias_duracion(self):
        for rec in self:
            if rec.fecha_inicio_embarque and rec.fecha_fin_embarque:
                duracion = rec.fecha_fin_embarque - rec.fecha_inicio_embarque
                rec.duracion_dias = duracion.days

    @api.depends('fecha_inicio_embarque', 'duracion_dias')
    def _calcular_periodo_caducidad(self):
        for rec in self:
            if rec.fecha_inicio_embarque and rec.duracion_dias:
                rec.fecha_fin_embarque = rec.fecha_inicio_embarque + relativedelta(days=+rec.duracion_dias)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self._get_seq_with_company("permiso_provisional_embarque_code") #self.env["ir.sequence"].next_by_code("permiso_provisional_embarque_code")

            if 'documento_emitido_id' in vals:
                documento_emitido_id = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
                vals['personal_maritimo_id'] = documento_emitido_id.personal_maritimo_id.id
                vals['jerarquia_id'] = documento_emitido_id.tramite_id.id
                vals['tipo_permiso_id'] = documento_emitido_id.tramite_id.tipo_permiso_id.id
        return super().create(vals_list)

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Permiso provisional de embarque debe ser único.')
    ]
