from odoo import api, fields, models, _

class OwnerMatricula(models.Model):
    _name = 'sigmap.owner.matricula'
    _description = _('Registration Number Owner')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # reparto_emision_id
    reparto_id = fields.Many2one(
        'sigmap.reparto',
        ondelete='restrict',
        string=_('Related Distribution'),
        required=True,
        copy=False,
        tracking=True)

    fecha_emision = fields.Date(
        string=_('Issue Date'),
        required=True,
        copy=False,
        tracking=True)

    fecha_caducidad = fields.Date(
        string=_('Expiry Date'),
        required=True,
        copy=False,
        tracking=True)
  
    numero_formato = fields.Char(
        string=_('Format Number'),
        required=True,
        copy=False,
        tracking=True)

    codigo_documento = fields.Char(
        string=_('Document Code'),
        required=True,
        copy=False,
        tracking=True)
    
    fecha_ultima_impresion = fields.Date(
        string=_('Last printed Date'),
        required=False,
        copy=False,
        tracking=True)

    num_impresiones = fields.Integer(
        string=_('Printed times number'),
        required=False,
        copy=False,
        tracking=True)

    # estado [ A | I ]
    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)
