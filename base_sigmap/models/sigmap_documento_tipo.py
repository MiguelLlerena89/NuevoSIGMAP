
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError

class SigmapDocumentoTipo(models.Model):
    _name = "sigmap.documento.tipo"
    _description = "Tipo de documento en SIGMAP"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string=_('Nombre'))
    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)