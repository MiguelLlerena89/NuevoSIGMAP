from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_ec_auth = fields.Many2one("l10n_ec.sri.autorizacion")
    l10n_ec_entity = fields.Char(related="")
    l10n_ec_emission = fields.Char(related="")
