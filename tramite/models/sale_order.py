from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from dateutil.relativedelta import relativedelta

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    res_partner_multa_id = fields.Many2one(
        'citacion.multa',
        string=_('DIRNEA Penalty'))

    discount = fields.Float(
        compute="_check_tiene_descuento"
    )

    @api.depends('order_partner_id')
    def _check_tiene_descuento(self):
        for line in self:
            if line.order_partner_id.aplica_descuento:
                line.discount = 50
            else:
                line.discount = 0


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tipo = fields.Selection([
            ("persona_mar","Persona de Mar"),
            ("nave","Nave"),
            ("trafico_maritimo","Tráfico Marítimo"),
        ], string=_("Tipo de solicitud"), default="persona_mar", tracking=True)
    tipo_documento_id = fields.Many2one("sigmap.documento.tipo", string=_("Tipo de solicitud"), required=True, tracking=True, store=True)
    tipo_reparto_id = fields.Many2one("sigmap.reparto.tipo", string=_("Tipo de Reparto"), tracking=True, store=True)
    reparto_id = fields.Many2one("sigmap.reparto", string="Reparto", default=lambda self: self.env.user.reparto_id, readonly=True, tracking=True, store=True)
    tramite_ids = fields.One2many(
        "tramite",
        inverse_name="order_id",
        string=_("Trámites"),
        tracking=True,
        store=True
    )
    order_line = fields.One2many(compute="_compute_order_line_ids", store=True)
    beneficiario_id = fields.Many2one(
        "personal.maritimo",
        string=_("Beneficiario"),
        tracking=True,
    )
    partner_id = fields.Many2one(
        domain=['|', ('active', '=', True), ('active', '=', False)],
        context={'active_test': False}
    )
    beneficiario_nave_id = fields.Many2one(
        "res.partner",
        string=_("Beneficiario"),
        tracking=True,
    )
    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Nave'),
        store=True,
        tracking=True)
    state = fields.Selection(
        selection=[
            ('draft', "Esperando confirmación"),
            ('sent', "Esperando pago"),
            ('sale', "Verificando pago"),
            ('done', "Facturado"),
            ('cancel', "Anulado"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    email = fields.Char('Correo', compute="_compute_email", store=True, readonly=False)
    aplica_descuento = fields.Boolean(related='partner_id.aplica_descuento')
    fallecido = fields.Boolean(related='partner_id.fallecido')
    antecedentes_penales = fields.Boolean(related='partner_id.antecedentes_penales')
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)


    validity_date = fields.Date(
        compute="_calcular_periodo_caducidad",
    )

    @api.depends('date_order')
    def _calcular_periodo_caducidad(self):
        for rec in self:
            if rec.date_order:
                params = self.env['ir.config_parameter'].sudo()
                periodo_caducidad = params.get_param("tramite.tiempo_maximo_validez_solicitudes")
                rec.validity_date = rec.date_order + relativedelta(days=+int(periodo_caducidad))

    @api.depends('beneficiario_id', 'beneficiario_nave_id', 'partner_id')
    def _compute_email(self):
        for order in self:
            order.email = False
            if order.beneficiario_id:
                order.email = order.beneficiario_id.email
            elif order.beneficiario_nave_id:
                order.email = order.beneficiario_id.email
            else:
                order.email = order.partner_id.email


    @api.onchange("tipo_documento_id")
    def _onchange_tipo_documento_id(self):
        if self.tipo_documento_id:
            self.beneficiario_id = None
            self.beneficiario_nave_id = None
            self.nave_id = None
        delete_prod_rows = []
        for line in self.order_line:
            delete_prod_rows.append((2, line.id))
        self.write({"order_line": delete_prod_rows})

    @api.onchange("beneficiario_id")
    def _onchange_beneficiario_id(self):
        if self.fallecido:
            raise ValidationError('Persona no puede solicitar ningún servicio.')
        if not self.beneficiario_id:
            return
        if self.beneficiario_id.sancion_activa:
            return {
                'warning': {
                    'title': _('Persona tiene una sanción.'),
                    'message': _("No se puede crear una solicitud de la persona seleccionada."
                                 " Informarle al usuario.")
                }
            }

    @api.depends("tramite_ids", "tipo_documento_id", "partner_id")
    def _compute_order_line_ids(self):
        delete_prod_rows = []
        for line in self.order_line:
            delete_prod_rows.append((2, line.id))
        self.write({"order_line": delete_prod_rows})
        rubros = []
        if self.tipo_documento_id and self.partner_id:
            if self.env.ref('base_sigmap.citacion').id == self.tipo_documento_id.id:
                multas = self.partner_id._get_multas_a_pagar()
                lines = []
                for multa in multas:
                    lines.append((0, 0, {
                        "product_id": multa['product_id'],
                        "name": multa['description'],
                        "product_uom_qty": 1,
                        "price_unit": multa['value'],
                    }))
                self.write({"order_line": lines})
                return
        for tramite in self.tramite_ids:
            rubros = []
            for rubro in tramite.rubro_ids:
                cantidad = 1
                if tramite.cantidad:
                    cantidad = tramite.cantidad
                #product = self.env['product.product'].search([('product_tmpl_id','=',rubro.product_id.id)])
                data = {
                    "product_id": rubro.product_id.product_variant_id.id,
                    "product_uom_qty": cantidad,
                    "price_unit": rubro.monto,
                }
                if tramite.jerarquia_id and rubro.product_id:
                    data['name'] = rubro.product_id.name + ' ' + tramite.jerarquia_id.name
                rubros.append((0, 0, data))
            self.write({"order_line": rubros})


    def _prepare_invoice(self):

        if self.fallecido:
            raise ValidationError('Persona no puede solicitar ningún servicio.')

        confirm = super()._prepare_invoice()
        if confirm:
            for tramite in self.tramite_ids:
                tramite.state = "invoiced"
        return confirm

    def action_confirm(self):
        #if self.beneficiario_id:
        #    if not self.beneficiario_id.image_1920 and not self.beneficiario_id.image_firma:
        #        raise ValidationError(_('Por favor actualice la foto y la firma del beneficiario'))
        # Pendiente volver a activar

        if self.fallecido:
            raise ValidationError('Persona no puede solicitar ningún servicio.')

        if self.state == 'draft' and self.partner_id.tipo_juridica != 'publica':
            raise ValidationError('Se tiene que pagar la solicitud primero.')

        return super().action_confirm()

    def action_pagado(self):
        pass

    def action_entregado(self):
        for tramite in self.tramite_ids:
            tramite.state = "sent"

    def action_send_email(self):

        if self.fallecido:
            raise ValidationError('Persona no puede solicitar ningún servicio.')
        self.ensure_one()
        mail_template = self.env.ref('tramite.email_template_sale_tramite')
        print(mail_template)
        mail_template.send_mail(self.id, force_send=True)


    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            self.action_send_email()
