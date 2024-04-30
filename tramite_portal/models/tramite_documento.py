from odoo import fields, models, _


class TramiteDocumento(models.Model):
    _inherit = "tramite.documento"

    portal = fields.Boolean(string=_("Disponible en portal?"), default=False)
