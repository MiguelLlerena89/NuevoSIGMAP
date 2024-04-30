# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class SRIFormaPagoTipo(models.Model):
    _name = "sri.payment.type"

    name = fields.Char(string='Nombre', index=True, copy=False)
    forma_pago_id = fields.Many2one('l10n_ec.sri.payment', 'Forma de pago')

class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    forma_pago_id = fields.Many2one('l10n_ec.sri.payment', 'Forma de pago')

class SRIEstablecimiento(models.Model):
    _name = 'l10n_ec.sri.establecimiento'
    _rec_name = 'code'
    _description = 'Establecimiento'

    def _default_partner(self):
        partner = self.env.user.company_id.partner_id
        return partner

    def _default_company(self):
        return self.env.user.company_id

    name = fields.Char('Nombre', related='partner_id.name')
    address = fields.Char('Dirección', size=100, related='partner_id.street')
    code = fields.Char('Código', size=3, required=True)
    partner_id = fields.Many2one('res.partner', 'Institución', default=_default_partner)
    l10n_ec_business_name = fields.Char(_('Nombre comercial'), related='partner_id.l10n_ec_business_name')
    punto_emision_ids = fields.One2many('l10n_ec.sri.punto.emision', 'establecimiento_id', 'Pos')
    company_id = fields.Many2one('res.company', string=_('Institución'), default=_default_company)

    def check_vat(self, vat):
        if not vat:
            raise ValidationError(_('No ha configurado el RUC de la compañía'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            partner_id = vals.get('partner_id')
            partner = self.env['res.partner'].browse(partner_id)
            self.check_vat(partner.vat)
        return super().create(vals_list)

    def write(self, vals):
        if self.partner_id:
            partner = self.partner_id
        else:
            partner_id = vals.get('partner_id')
            partner = self.env['res.partner'].browse(partner_id)
        self.check_vat(partner.vat)
        return super().write(vals)

    _sql_constraints = [
        ('establecimiento_unique', 'unique(partner_id,code,company_id)', u'Establecimiento debe ser único.'),
        ]

class SRIPos(models.Model):
    _name = 'l10n_ec.sri.punto.emision'
    _rec_name = 'code'
    _description = 'Punto de emisión'

    code = fields.Char('Pos', size=3, required=True)
    establecimiento_id = fields.Many2one('l10n_ec.sri.establecimiento', 'Establecimiento')
    documento_ids = fields.One2many('l10n_ec.sri.autorizacion', 'punto_emision_id', 'Pos')

    @api.onchange('code')
    def onchange_code(self):
        if not self.establecimiento_id.code:
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _('Debe definir código de establecimiento.'),
                }
            }

    def action_edit_docs_wizard(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Tipos de comprobantes'),
                'res_model': 'l10n_ec.sri.punto.emision',
                'target': 'new',
                'view_id': self.env.ref('l10n_ec_sri.view_punto_emision_form').id,
                'view_mode': 'form',
                'res_id': self.id,
                }

class SRIAutorizacion(models.Model):
    _name = "l10n_ec.sri.autorizacion"
    _description = 'Autorización'
    _rec_name = 'numero'

    def _default_partner(self):
        if self._context.get('autorizacion_tipo') == 'out':
            partner = self.env.user.company_id.partner_id
            return partner
        elif self._context.get('partner_id'):
            partner = self._context.get('partner_id')
            return partner

    def _default_company(self):
        return self.env.user.company_id

    def _default_estab(self):
        if self._context.get('autorizacion') == 'out':
            code = self.establecimiento_id.code
            return code

    def _default_pos(self):
        if self._context.get('autorizacion') == 'out':
            code = self.punto_emision_id.code
            return code

    name = fields.Char(_("Autorización"), translate=True)
    company_id = fields.Many2one('res.company', string=_('Company'), default=_default_company)
    numero = fields.Char('Número de autorización', size=128, copy=False)
    establecimiento_id = fields.Many2one('l10n_ec.sri.establecimiento', 'Establecimiento', copy=False)
    punto_emision_id = fields.Many2one('l10n_ec.sri.punto.emision', 'pos')
    # establecimiento = fields.Char('Establecimiento código', related='punto_emision_id.establecimiento_id.code', copy=False, size=3)
    # punto_emision = fields.Char('Punto de emisión', related='punto_emision_id.code', size=3)
    establecimiento = fields.Char('Establecimiento código', copy=False, size=3, default=_default_estab)
    punto_emision = fields.Char('Punto de emisión', size=3, default=_default_pos)
    sequence_start = fields.Integer('Secuencia inicial')
    sequence_end = fields.Integer('Secuencia final')
    start_date = fields.Date('Fecha inicio')
    expiration_date = fields.Date('Fecha expiración')
    active = fields.Boolean('Activo?', default=True)
    is_electronic = fields.Boolean('Documento Electrónico?', default=True)
    l10n_latam_document_type_id = fields.Many2one(
        'l10n_latam.document.type',
        'Tipo de comprobante',
        required=True
        )
    code = fields.Char('Código comprobante', related='l10n_latam_document_type_id.code')
    autorizacion_tipo = fields.Selection([
            ('in',''),
            ('out','Out'),
            ], index=True, change_default=True,
        default=lambda self: self._context.get('autorizacion_tipo', 'out'),
        )

    partner_id = fields.Many2one(
        'res.partner',
        'Empresa',
        default=_default_partner
        )
    sequence_id = fields.Many2one(
        'ir.sequence',
        'Secuencia',
        help='Secuencia alfanumérica',  # noqa
        ondelete='cascade'
        )
    sequence = fields.Integer('Secuencia', related='sequence_id.number_next_actual', readonly=False, copy=False)

    _sql_constraints = [
        ('numero_unique', 'unique(partner_id,expiration_date,l10n_latam_document_type_id)', u'Número de autorización, fecha expiración y tipo es única para la misma empresa.'),  # noqa
        ('numero_unique', 'unique(partner_id,numero, autorizacion_tipo, l10n_latam_document_type_id, punto_emision, establecimiento)', 'Autorización es única para la misma empresa!'),
        ]

    def check_vat(self, vat):
        if not vat:
            raise ValidationError(_('No ha configurado el RUC de la compañía'))

    @api.model
    def create(self, vals):
        partner_id = vals.get('partner_id')
        partner = self.env['res.partner'].browse(partner_id)
        self.check_vat(partner.vat)
        auth = super(SRIAutorizacion, self).create(vals)

        if vals.get('autorizacion_tipo') == 'out':
            auth.establecimiento = auth.punto_emision_id.establecimiento_id.code
            auth.punto_emision = auth.punto_emision_id.code
            auth.numero = auth.establecimiento + auth.punto_emision + '0000'
            auth.sequence_id = self.sudo()._create_sequence(vals).id
            auth.establecimiento_id = auth.punto_emision_id.establecimiento_id.id
        return auth

    def write(self, vals):
        if self.partner_id:
            partner = self.partner_id
        else:
            partner_id = vals.get('partner_id')
            partner = self.env['res.partner'].browse(partner_id)
        self.check_vat(partner.vat)
        auth = super(SRIAutorizacion, self).write(vals)
        if self.autorizacion_tipo == 'out':
            if not self.sequence_id:
                if 'numero' not in vals:
                    vals['numero'] = self.numero
                self.sequence_id = self.sudo()._create_sequence(vals).id
        return auth


    @api.onchange('numero')
    def validate_authorisation_numero(self):
        # Only physical authorisation have a number and must be ten digits
        if not self.is_electronic and self.numero and len(self.numero) != 10:
            raise UserError(_(
                u'Debe ingresar 10 dígitos según el documento.')
            )

    @api.model
    def _create_sequence(self, vals):
        """ Create new no_gap entry sequence for every new Journal"""
        autorizacion_tipo = self.env['l10n_latam.document.type'].search([('id', '=', vals.get('l10n_latam_document_type_id', self.l10n_latam_document_type_id.id))], limit=1)
        if vals.get('is_electronic', self.is_electronic):
            is_elect = _(' ELECTRONICA ')
        else:
            is_elect = _(' FISICA ')

        if 'numero' not in vals:
            if not vals['numero']:
                vals['numero'] = vals['establecimiento'] + vals['punto_emision'] +  autorizacion_tipo.code
        else:
            vals['numero'] = ''

        seq = {
            'name': autorizacion_tipo.name.upper() + is_elect + vals['numero'],
            'implementation': 'standard',
            'padding': 9,
            'number_increment': 1,
            'use_date_range': False,
        }
        seq['company_id'] = vals.get('company_id', self.company_id.id)
        return self.env['ir.sequence'].create(seq)

    @api.depends('name', 'l10n_latam_document_type_id', 'numero')
    def name_get(self):
        result = []
        for auth in self:
            name = auth.name
            if auth.l10n_latam_document_type_id and auth.numero:
                name = '%s - %s' % (auth.l10n_latam_document_type_id.name, auth.numero)
            result.append((auth.id, name))
        return result
