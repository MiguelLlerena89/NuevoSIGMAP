from odoo import api, fields, models, _

class TipoRango(models.Model):
    _name = 'tipo.rango'
    _description = 'Tipo de Rango'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True)
    descripcion = fields.Char('Descripción')
    abreviatura = fields.Char('Abreviatura', required=True)
    fuerza = fields.Selection([
        ('N', 'NAVAL'),
        ('A', 'ÁEREA'),
        ('T', 'TERRESTRE'),
    ], string='Fuerza', required=True, index=True, copy=False, tracking=True)
    active = fields.Boolean(_('Active?'), default=True)

    _sql_constraints = [
        ('name_fuerza_uniq', 'unique (name,fuerza)', 'El tipo de rango ya existe!!')
    ]