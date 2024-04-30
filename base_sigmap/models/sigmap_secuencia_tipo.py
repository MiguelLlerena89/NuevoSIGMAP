from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError

class SigmapSecuenciaTipo(models.Model):
    _name = "sigmap.secuencia.tipo"
    _description = "Tipo de Secuencia por documentos en SIGMAP"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string=_('Nombre'))
    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)