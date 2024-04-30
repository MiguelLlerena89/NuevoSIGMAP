# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import itertools

class AccountMove(models.Model):
    _inherit = "account.move"

    COMPROBANTE_TIPO = {
            'out_invoice': '01',
            'in_invoice': '01',
            }

    def _default_autorizacion(self):
        if 'default_move_type' not in self.env.context:
            return False
        move_type = self.env.context['default_move_type']
        if move_type in ['out_invoice']:
            code = self.COMPROBANTE_TIPO[move_type]
            auth = self.env['l10n_ec.sri.autorizacion'].search([('autorizacion_tipo', '=', 'out'), ('code','like', code), ('partner_id', '=', self.env.user.company_id.partner_id.id)], limit=1)
            return auth
        elif move_type in ['in_invoice']:
            code = self.COMPROBANTE_TIPO[move_type]
            auth = self.env['l10n_ec.sri.autorizacion'].search([('autorizacion_tipo', '=', 'in'), ('code','like', code), ('partner_id', '=', self.partner_id.id)], limit=1)
        else:
            return False

    def _get_sri_punto_emision_id_domain(self):
        res = [('id', '=', 0)]
        return res

    l10n_latam_internal_type = fields.Selection(
        related="l10n_latam_document_type_id.internal_type",
        string="Tipo comprobante",
        store=True,
    )

    invoice_date = fields.Date(default=fields.Date.today)
    comprobante_id = fields.Many2one('l10n_ec.sri.comprobante', string="Comprobante", copy=False)
    comprobante_state = fields.Selection(related='comprobante_id.state', string="Estado SRI", copy=False)
    comprobante_document_type = fields.Char(related='comprobante_id.l10n_latam_document_type_id.name', string="Tipo Documento", copy=False)
    secuencial = fields.Char(string=_('Secuencial'), size=9, index=True, copy=False)
    numero = fields.Char(related="comprobante_id.numero", string=_('Número'), size=15, store=True, copy=False)
    sri_autorizacion_id = fields.Many2one('l10n_ec.sri.autorizacion', string=_('Autorización'), copy=False, default=_default_autorizacion)
    # Cambiar nombre de campo EOD
    sri_aut_eod_id = fields.Many2one(related='sri_autorizacion_id.partner_id')
    sri_aut_vat = fields.Char(related='sri_autorizacion_id.partner_id.vat')
    fecha_vencimiento_certificado = fields.Date(related='company_id.certificate_not_valid_after')
    sri_numero_autorizacion = fields.Char(string=_('Numero Autorización'), size=49, index=True, compute='compute_sri_numero_autorizacion', copy=False)
    sri_establecimiento_id = fields.Many2one("l10n_ec.sri.establecimiento")
    sri_punto_emision_id = fields.Many2one("l10n_ec.sri.punto.emision")
    sri_establecimiento = fields.Char(string=_('Establecimiento'), size=3, index=True, compute='compute_sri_serie')
    sri_punto_emision = fields.Char(string=_('Punto Emisión'), size=3, index=True, compute='compute_sri_serie')
    is_electronic = fields.Boolean(string=_('Es electrónico?'), default=True, index=True)

    """ Totales según tabla 21. FICHA TÉCNICA COMPROBANTES ELECTRÓNICOS"""
    subtotal_iva = fields.Monetary(string='Subtotal IVA', store=True, readonly=True, copy=False, compute="compute_totales_impuestos")
    subtotal_iva_0 = fields.Monetary(string='Subtotal 0% IVA', store=True, readonly=True, copy=False, compute="compute_totales_impuestos")
    subtotal_no_iva = fields.Monetary(string='Subtotal no objeto IVA', store=True, readonly=True, copy=False, compute="compute_totales_impuestos")
    subtotal_exento_iva = fields.Monetary(string='Subtotal exento IVA', store=True, readonly=True, copy=False, compute="compute_totales_impuestos")
    subtotal = fields.Monetary(string='Subtotal', store=True, readonly=True, copy=False, compute="compute_totales_impuestos")
    total_descuento = fields.Monetary(string='Total descuento', store=True, readonly=True, copy=False, compute="compute_total_discount_amount")
    valor_ice = fields.Monetary(string='Valor ICE', store=True, readonly=True, copy=False)
    valor_irbpnr = fields.Monetary(string='Valor IRBPNR', store=True, readonly=True, copy=False)
    valor_iva = fields.Monetary(string='Valor IVA', store=True, readonly=True, copy=False, compute="compute_totales_impuestos")
    propina = fields.Monetary(string='Propina', store=True, readonly=True, copy=False)
    valor_total = fields.Monetary(string='Valor total', store=True, readonly=True, copy=False, compute="compute_totales_impuestos")

    subtotal_ret_ir = fields.Monetary(string='Monto retención IR', store=True, readonly=True, copy=False)
    subtotal_ret_iva = fields.Monetary(string='Monto retención IVA', store=True, readonly=True, copy=False)
    total_ret_ir = fields.Monetary(string='Total retenciones IR', store=True, readonly=True, copy=False)
    #TODO Retenciones IVA servicios y bienes. Se hace un total para cada una o uno solo?
    total_ret_iva = fields.Monetary(string='Total retenciones IVA', store=True, readonly=True, copy=False)
    total_ret = fields.Monetary(string='Total Retenciones', store=True, readonly=True, copy=False)
    valor_sin_impuestos = fields.Monetary(string='Sin impuestos', store=True, readonly=True, copy=False)
    valor_noret_ir = fields.Monetary(string='Monto no sujeto a IR', store=True, readonly=True, copy=False)

    #tabla escrita manualmente, Campo adicional (texto, valor)
    aditional_info_ids = fields.One2many('l10n_ec.sri.informacion.adicional', 'move_id', string="Campo adicional")
    #plan_pago_ids = fields.One2many('l10n_ec.sri.plan.pago', 'move_id', string=_('Plan de pago'), compute="_create_default_plan_pago_line_values", copy=False)
    plan_pago_ids = fields.One2many('l10n_ec.sri.plan.pago', 'move_id', string=_('Plan de pago'), copy=False)


    @api.depends('sri_autorizacion_id', 'sri_numero_autorizacion', 'is_electronic')
    def compute_sri_serie(self):
        if self.move_type in ['entry']:
            self.sri_establecimiento = False
            self.sri_punto_emision = False
            return
        if self.sri_autorizacion_id:
            self.sri_establecimiento = self.sri_autorizacion_id.establecimiento
            self.sri_punto_emision = self.sri_autorizacion_id.punto_emision
        elif self.sri_numero_autorizacion:
            self.sri_establecimiento = self.sri_numero_autorizacion[24:27]
            self.sri_punto_emision = self.sri_numero_autorizacion[27:30]
        else:
            self.sri_establecimiento = False
            self.sri_punto_emision = False


    @api.depends('is_electronic', 'comprobante_id', 'sri_autorizacion_id')
    def compute_sri_numero_autorizacion(self):
        if self.move_type in ['entry']:
            self.sri_numero_autorizacion = False
            return
        if not self.is_electronic:
            if self.sri_autorizacion_id:
                self.sri_numero_autorizacion = self.sri_autorizacion_id.numero
            else:
                self.sri_numero_autorizacion = False
        else:
            if self.comprobante_id and self.comprobante_id.numero_autorizacion:
                self.sri_numero_autorizacion = self.comprobante_id.numero_autorizacion
            else:
                self.sri_numero_autorizacion = False

    @api.onchange('partner_id')
    def set_authorisation_id_domain(self):
        if self.move_type in ('out_invoice','in_invoice'):
            code = self.COMPROBANTE_TIPO[self.move_type]
            domain = [('autorizacion_tipo', '=', self.move_type.split('_')[0]),('code','like', code),('is_electronic', '=', bool(self.is_electronic))]
            if self.move_type.startswith('out_'):
                partner = self.company_id.partner_id.id
            else:
                partner = self.partner_id.id
            domain_partner= ('partner_id', '=', partner)
            domain.append(domain_partner)
            return {'domain': {'sri_autorizacion_id': domain}}

    @api.onchange('sri_autorizacion_id')
    def onchange_sri_autorizacion_id(self):
        if self.move_type in ['entry']:
            return
        if self.sri_autorizacion_id:
            self.is_electronic = self.sri_autorizacion_id.is_electronic
            if not self.sri_autorizacion_id.is_electronic:
                self.sri_numero_autorizacion = self.sri_autorizacion_id.numero
            if self.move_type.startswith('out_'):
                self.secuencial = self.sri_autorizacion_id.sequence_id.number_next_actual
                if not self.sri_establecimiento_id:
                    self.sri_establecimiento_id = self.sri_autorizacion_id.establecimiento_id
                    self.sri_punto_emision_id = self.sri_autorizacion_id.punto_emision_id
            else:
                if self.secuencial:
                    self.secuencial = self.secuencial.zfill(9)

    @api.onchange('sri_establecimiento_id')
    def set_sri_punto_emision_id_domain(self):
        #self.sri_punto_emision_id = None
        if self.move_type in ['entry']:
            return
        if self.sri_establecimiento_id:
            return { 'domain' : { 'sri_punto_emision_id': [('id','in',self.sri_establecimiento_id.punto_emision_ids.ids)]}}
        return {}

    @api.onchange('sri_punto_emision_id')
    def onchange_sri_punto_emision_id(self):
        if self.move_type in ['entry']:
            return
        if self.is_electronic and self.sri_establecimiento_id:
            code = self.COMPROBANTE_TIPO[self.move_type]
            domain = [('autorizacion_tipo', '=', self.move_type.split('_')[0]),('code','like', code),('establecimiento_id','=', self.sri_establecimiento_id.id),('punto_emision_id','=', self.sri_punto_emision_id.id)]
            if self.move_type.startswith('out_'):
                partner = self.company_id.partner_id.id
            else:
                partner = self.partner_id.id
            domain_partner= ('partner_id', '=', partner)
            domain.append(domain_partner)
            autorizacion_id = self.env['l10n_ec.sri.autorizacion'].search(domain)
            if autorizacion_id:
                self.sri_autorizacion_id = autorizacion_id
                self.onchange_sri_autorizacion_id()
            elif self.sri_punto_emision_id:
                msg = _('No se ha configurado una autorización de %s para establecimiento: %s y punto de emisión: %s') % (self.type_name, self.sri_establecimiento_id.code, self.sri_punto_emision_id.code),
                self.secuencial = ''
                self.sri_punto_emision_id = None
                return {
                    'warning': {
                        'title': _('Warning!'),
                        'message': msg,
                    }
                }

    @api.depends('invoice_line_ids.product_id')
    def _create_informacion_adicional_line_values(self):
        for rec in self:
            if rec.move_type in ('out_invoice'):
                inf_addicional = []
                for line in rec.invoice_line_ids:
                    if line.product_id:
                        data = {
                            'adicional_nombre': line.product_id.name,
                            'adicional_valor': line.name,
                            }
                    else:
                        data = {
                            'adicional_nombre': 'Facturación',
                            'adicional_valor': line.name,
                            }
                    inf_addicional.append((0, 0, data))
                rec.write({'aditional_info_ids': inf_addicional})
            else:
                rec.aditional_info_ids = False

    @api.depends('invoice_line_ids','invoice_payment_term_id')
    def _create_default_plan_pago_line_values(self):
        for rec in self:
            if rec.move_type in ('out_invoice'):
                if rec.amount_total != 0:
                    plazo = rec.invoice_payment_term_id.line_ids[0].days if rec.invoice_payment_term_id else 0
                    data = {
                            # Ver qué forma de pago usar?
                            'forma_pago_id': self.env.ref('l10n_ec.P20').id,
                            'plazo': plazo,
                            'total': rec.amount_total,
                            'unidad_tiempo_id': self.env.ref('uom.product_uom_day').id,
                            }
                    rec.write({'plan_pago_ids': [(0, 0, data)]})
                else:
                    rec.plan_pago_ids = False
            else:
                rec.plan_pago_ids = False

    def action_comprobante(self):
        if self.comprobante_id:
            self.comprobante_id.write({
                'establecimiento': self.sri_establecimiento,
                'punto_emision': self.sri_punto_emision,
                'sri_autorizacion_id': self.sri_autorizacion_id.id
                })
            return False
        data = {
            'company_id': self.company_id.id,
            'partner_id': self.partner_id.id,
            'sri_autorizacion_id': self.sri_autorizacion_id.id,
            'type': self.move_type.split('_')[0],
            'is_electronic': self.is_electronic,
            'fecha_emision': self.invoice_date,
            'ambiente': self.company_id.ambiente,
            'tipo_emision': self.company_id.tipo_emision,
            'l10n_latam_document_type_id': self.sri_autorizacion_id.l10n_latam_document_type_id.id,
            'establecimiento': self.sri_establecimiento,
            'punto_emision': self.sri_punto_emision,
            'secuencial': self.secuencial.zfill(9),
            'move_id' : self.id,
            'state': 'NEW'
        }
        if not self.is_electronic:
            data['numero_autorizacion'] = self.sri_autorizacion_id.numero
        comprobante = self.env['l10n_ec.sri.comprobante'].create(data)
        self.comprobante_id = comprobante.id
        comprobante.action_auth_XML()
        return True


    def validate_account_move(self):
        msg = ''
        if self.is_electronic:
            if self.move_type in ['out_invoice','out_refund']:
                if not self.sri_establecimiento_id:
                    msg = msg + 'Debe definir un establecimiento.\n'
                if not self.sri_punto_emision_id:
                    msg = msg + 'Debe definir un punto de emisión.\n'
                if not self.sri_autorizacion_id:
                    msg = msg + ('No existe autorización para esta %s.\n') % (self.type_name)
            elif self.move_type in ['in_invoice', 'in_refund']:
                if not self.sri_establecimiento:
                    msg = msg + 'Debe definir un establecimiento.\n'
                if not self.sri_punto_emision:
                    msg = msg + 'Debe definir un punto de emisión.\n'
        else:
            if self.move_type in ['in_invoice']:
                if not self.sri_autorizacion_id:
                    msg = msg + ('Debe seleccionar una autorización para esta %s.\n') % (self.type_name)
                else:
                    if (int(self.secuencial) < self.sri_autorizacion_id.sequence_start) or (int(self.secuencial) > self.sri_autorizacion_id.sequence_end):
                        msg = msg + ('Número de secuencial ingresado es incorrecto. Fuera de rango permitido.\n')
                    if self.invoice_date > self.sri_autorizacion_id.expiration_date:
                        msg = msg + ('La fecha de emisión es incorrecto. Excede a la fecha de vencimiento permitida.\n')
                if not self.sri_establecimiento:
                    msg = msg + 'Debe definir un establecimiento.\n'
                elif self.sri_establecimiento != self.sri_autorizacion_id.establecimiento:
                    msg = msg + 'Inconsistencia establecimiento.\n'
                if not self.sri_punto_emision:
                    msg = msg + 'Debe definir un punto de emisión.\n'
                elif self.sri_punto_emision != self.sri_autorizacion_id.punto_emision:
                    msg = msg + 'Inconsistencia de punto de emisión.\n'
        if msg:
            raise UserError(_(msg))
        return True

    def action_post(self):
        if self.move_type not in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'):
            return super().action_post()

        #refuse to validate a vendor bill/refund if there already exists one with the same document_sequence for the same partner,
        #because it's probably a double encoding of the same bill/refund
        if self.move_type in ('in_invoice', 'in_refund') and self.secuencial:
            if self.search([('move_type', '=', self.move_type), ('secuencial', '=', self.secuencial), ('sri_establecimiento', '=', self.sri_establecimiento), ('sri_punto_emision', '=', self.sri_punto_emision), ('sri_numero_autorizacion', '=', self.sri_numero_autorizacion), ('company_id', '=', self.company_id.id), ('state', 'in', ['posted']), ('commercial_partner_id', '=', self.commercial_partner_id.id),('is_electronic', '=', self.is_electronic)]):
                raise UserError(_("Se ha detectado secuencial duplicado para el mismo proveedor."))

        self._create_default_plan_pago_line_values()
        self._create_informacion_adicional_line_values()
        self.validate_account_move()
        res = super().action_post()
        if self.move_type.startswith('out_') and self.state == 'posted':
            if not self.comprobante_id:
                self.secuencial = self.sri_autorizacion_id.sequence_id.next_by_id().zfill(9)
            self.action_comprobante()

        return res

    @api.depends('invoice_line_ids.discount', 'currency_id', 'company_id')  # noqa
    def compute_total_discount_amount(self):
        for move in self:
            move.total_descuento = 0
            for line in self.invoice_line_ids:
                priced = line.price_unit * (1 - (line.discount or 0.00) / 100.0)
                move.total_descuento += (line.price_unit - priced) * line.quantity

    @api.depends('invoice_line_ids.tax_ids', 'invoice_line_ids.price_subtotal', 'currency_id', 'company_id')  # noqa
    def compute_totales_impuestos(self):
        for move in self:
            tax_list = []
            for line in move.invoice_line_ids:
                for tax_line in line.tax_ids:
                    tax_list.append((tax_line, line.price_subtotal))

            move.subtotal = 0
            move.subtotal_iva = 0
            move.valor_iva = 0
            move.subtotal_iva_0 = 0
            move.subtotal_no_iva = 0
            move.valor_noret_ir = 0
            move.valor_ice = 0
            move.valor_noret_ir = 0
            move.valor_ice = 0
            move.subtotal_ret_iva = 0
            move.total_ret_iva = 0
            move.subtotal_ret_iva = 0
            move.total_ret_iva = 0
            move.subtotal_ret_ir = 0
            move.total_ret_ir = 0

            for tax_group, tax_data in itertools.groupby(sorted(tax_list, key=lambda e: e[0].tax_group_id.id), key=lambda e: e[0].tax_group_id):
                tax = list(tax_data)
                group_code = tax_group.get_external_id()[tax_group.id].split('.')[1]

                move.subtotal_iva += sum(e[1] for e in tax if  group_code == 'vat')
                move.valor_iva += sum(e[0].amount * e[1]/100 for e in tax if  group_code == 'vat')
                move.subtotal_iva_0 += sum(e[1] for e in tax if group_code == 'vat0')
                move.subtotal_no_iva += sum(e[1] for e in tax if group_code == 'notvat')
                move.valor_noret_ir += sum(e[1] for e in tax if group_code == 'no_ret_ir')
                move.valor_ice += sum(e[1] for e in tax if group_code == 'ice')
                move.subtotal_ret_iva += sum(e[1] for e in tax if group_code == 'ret_vat_b')
                move.total_ret_iva += sum(e[0].amount * e[1]/100 for e in tax if group_code == 'ret_vat_b')
                move.subtotal_ret_iva += sum(e[1] for e in tax if group_code == 'ret_vat_srv')
                move.total_ret_iva += sum(e[0].amount * e[1]/100 for e in tax if group_code == 'ret_vat_srv')
                move.subtotal_ret_ir += sum(e[1] for e in tax if group_code  in ['AIR_res', 'AIR_no_res'])
                move.total_ret_ir += sum(e[0].amount * e[1]/100 for e in tax if group_code in ['AIR_res', 'AIR_no_res'])

            move.subtotal = move.subtotal_iva + move.subtotal_iva_0 + move.subtotal_no_iva
            move.valor_total = move.subtotal + move.valor_iva

    def button_cancel(self):
        if self.move_type not in ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'):
            super().button_cancel()
        if self.comprobante_id:
            self.comprobante_id.state = 'NUL'

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    def get_discount_amount(self):

        priced = self.price_unit * (1 - (self.discount or 0.00) / 100.0)
        discount = (self.price_unit - priced) * self.quantity
        return discount

class AccountMoveAditionalInfo(models.Model):
    _name = "l10n_ec.sri.informacion.adicional"

    move_id = fields.Many2one('account.move', string=_('Move'), index=True, copy=False)
    adicional_nombre = fields.Char(string=_('Nombre'), size=50, copy=False)
    adicional_valor = fields.Char(string=_('Valor'), size=100, copy=False)
