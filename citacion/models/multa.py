from odoo import api, fields, models, _

class Multa(models.Model):
    _name = 'citacion.multa'
    _description = _( 'Penalty')
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sigmap.updated.by']

    READONLY_STATES = { state: [('readonly', True)] for state in ['paid', 'canceled']}

    state = fields.Selection(
        [
            ('analyzing',_('analyzing')),
            ('notified',_('Notified')),
            ('in_challenge',_('In Challenge')),
            ('contested',_('Contested')),
            ('to_pay',_('Collection')),
            ('paid',_('Paid')),
            ('canceled',_('Canceled')),
        ],
        string=_('States'),
        default='analyzing',
        index=True,
        tracking=True)

    reparto_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Distribution'))

    evento_tipo = fields.Selection(
        [
            ('citation', _('Citation')),
            ('monitor', _('Monitoring')),
            ('legalization', _('Legalization'))
        ],
        string=_('Type'),
        default=_('citation'),
        index=True,
        required=True,
        tracking=True)

    citacion_id = fields.Many2one(
        'citacion.citacion',
        string=_('Citation'),
        copy=False,
        tracking=True)

    citacion_contravencion_ids = fields.One2many(related='citacion_id.contravencion_ids')

    more_comments = fields.Char(related='citacion_id.more_comments')

    aplica_concurrencia = fields.Boolean(
        string=_('Concurrency?'),
        copy=False,
        tracking=True)

    contraventor_id = fields.Many2one(
        'res.partner',
        string=_("Offender"))

    articulo_numeral_id = fields.Many2one(
        'citacion.contravencion.ley.num',
        string=_('Law Reference'),
        copy=False,
        tracking=True)

    aplica_reincidencia = fields.Boolean(string=_('Recidivism?'))

    value = fields.Float(string=_('Value'))


    def _get_product_domain(self):
        multa_category = self.env.ref('citacion.product_category_multa')
        if not multa_category or not multa_category.id:
            return [()]
        else:
            multa_category_id = multa_category.id
            return [('categ_id', '=', multa_category_id)]

    product_id = fields.Many2one(
        'product.product',
        string=_('Item'),
        copy=False,
        Tracking=True,
        domain=_get_product_domain)


    description = fields.Char(
        string=_('Description'),
        copy=False,
        Tracking=True)


    factura_id = fields.Many2one(
        'account.move',
        copy=False,
        Tracking=True,
        required=False
    )

    factura_numero = fields.Char(
        string=_('Invoice Nº'),
        related = 'factura_id.numero',
        required=False
    )


    @api.onchange('citacion_id')
    def _onchange_citacion_id(self):
        self.ensure_one()
        if not self.citacion_id:
            self.contraventor_id = False
        else:
            self.contraventor_id = self.citacion_id.offender_id.id

    def name_get(self):
        result = []
        for rec in self:
            name = _('Penalty Nº')
            name += ' [%s]' % (rec.id) if rec.id else ' [' + _('new') + ']'

            result.append((rec.id, name))

        return result

    def action_analyzing(self):
        self.write({'state': 'analyzing'})

    def action_notified(self):
        self.write({'state': 'notified'})

    def action_in_challenge(self):
        self.write({'state': 'in_challenge'})

    def action_contested(self):
        self.write({'state': 'contested'})

    def action_to_pay(self):
        self.write({'state': 'to_pay'})

    def action_paid(self):
        self.write({'state': 'paid'})

    def action_canceled(self):
        self.write({'state': 'canceled'})
