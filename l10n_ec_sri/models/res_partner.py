# -*- coding: utf-8 -*-
import time
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import (
    ValidationError,
    Warning as UserError
)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_ec_business_name = fields.Char(
        string=_('Trade Name'),
        required=False,
        readonly=False,
        help=_('Trade Name of the Company')
    )

    representante_legal_id = fields.Many2one(
        'res.partner',
        string=_('Legal Representative'),
        index=True)

    representante_legal_name = fields.Char(
        related='representante_legal_id.name',
        readonly=True,
        string=_('Legal Representative'),
        help=_('Name of the legal representative'))

    # No valida RUCs Sociedades Juridicas (S.A.S.) ej: 1793189549001
    @api.constrains("vat", "country_id")
    def check_vat(self):
        partner_to_skip_validate = self.env["res.partner"]
        for partner in self:
            if (
                partner.country_id.code == "EC"
                and partner.vat
                and len(partner.vat) == 13
                and partner.vat[2] == "9"
            ):
                partner_to_skip_validate |= partner
        return super(ResPartner, self - partner_to_skip_validate).check_vat()

    def write(self, values):
        for partner in self:
            if (
                partner.vat in ["9999999999", "9999999999999"]
                and not self.env.is_system()
                and (
                    "name" in values
                    or "vat" in values
                    or "active" in values
                    or "country_id" in values
                )
            ):
                raise UserError(_("No se puede modificar consumidor final"))
        return super(ResPartner, self).write(values)

    def unlink(self):
        for partner in self:
            if partner.vat in ["9999999999", "9999999999999"]:
                raise UserError(_("You cannot unlink final consumer"))
        return super(ResPartner, self).unlink()

