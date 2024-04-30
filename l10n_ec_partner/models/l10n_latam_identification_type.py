from odoo import models, fields


class L10nLatamIdentificationType(models.Model):
    _inherit = "l10n_latam.identification.type"

    l10n_ec_ats_code = fields.Char("ATS Code")
    l10n_ec_sri_code = fields.Char("Electronic Docs Code")
