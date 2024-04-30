from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class MatriculaControl(models.Model):
    _name = "matricula.control"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)

    name = fields.Char("Observación", required=True)
    fecha_impresion = fields.Datetime(
        string="Fecha impresión",
       copy=False,
        tracking=True,
        default=fields.Datetime.now
    )
    motivo_id = fields.Many2one("matricula.motivo", string="Control impresión", tracking=True)
    motivo = fields.Selection([
        ('holograma_dañado', 'Se dañó el holograma'),
        ('cita_dañada', 'Se dañó la cinta'),
        ('pvc_cinta_dañada', 'Se dañó PVC y cinta'),
        ('pvc_holograma_dañada', 'Se dañó PVC y holograma'),
        ('cinta_holograma_dañada', 'Se dañó cinta y holograma'),
        ('material_dañado', 'Se dañó todo el material'),
        ('prueba_impresion', 'Prueba impresión'),
        ('ascenso', 'Ascenso'),
        ('cambio_especialidad', 'Cambio especialidad'),
        ('canje', 'Canje'),
        ('especialidad_alternativa', 'Especialidad alternativa'),
        ('primera_vez', 'Primera vez'),
        ('renovacion', 'Renovación'),
        ('reposicion', 'Reposición'),
    ], string='Control impresión', index=True, copy=False, tracking=True)
    motivo_reimpresion = fields.Text('Descripción del Motivo de Reimpresión')
    control_suministros_ids = fields.One2many("matricula.control.suministro", "control_id", string="Control", tracking=True)


class MatriculaControlSuministro(models.Model):
    _name = "matricula.control.suministro"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)

    name = fields.Char("Observación", required=True)
    control_id = fields.Many2one("matricula.control", string="Control", tracking=True)
    fecha_impresion = fields.Datetime(related="control_id.fecha_impresion", tracking=True)
    motivo_id = fields.Many2one(related="control_id.motivo_id", tracking=True)
    company_id = fields.Many2one(related="control_id.company_id", tracking=True)
    suministro_id = fields.Many2one("suministro", string="Control", tracking=True)
    cantidad = fields.Integer(string='Cantidad', copy=False, tracking=True, required=True)
    unidad_id = fields.Many2one('uom.suministro', string='Unidad de consumo', copy=False, tracking=True, required=True)
    fecha_ingreso = fields.Date(
        string="Fecha ingreso",
        index=True,
        copy=False,
        tracking=True,
        default=fields.Date.today
    )

    @api.model
    def create(self, vals):
        # Rebajar inventario
        vals['company_id'] = self.env.user.company_id.id
        if 'cantidad' in vals and 'suministro_id' in vals:
            control = self.env['control.suministro'].search([
                ('suministro_id', '=', vals['suministro_id']),
                ('company_id', '=', vals['company_id'])
                ], limit=1)
            if control:
                nuevo_registro = self.env['control.suministro'].create({
                    'suministro_id': vals['suministro_id'],
                    'company_id': vals['company_id'],
                    'unidad_id': vals['unidad_id'],
                    'cantidad': -1 * vals['cantidad'],
                    })
        return super().create(vals)


class MatriculaMotivo(models.Model):
    _name = "matricula.motivo"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("name", required=True)