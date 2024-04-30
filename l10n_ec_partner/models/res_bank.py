from odoo import models, fields, api, _


class ResBankAccountType(models.Model):
    _name = "res.bank.account.type"
    _description = "Bank Account Type"

    name = fields.Char(string='Bank account Type', required=True, translate=True)
    code = fields.Char(string='Bank account type code', required=True, translate=True)

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    acc_type = fields.Many2one('res.bank.account.type', string='Type')