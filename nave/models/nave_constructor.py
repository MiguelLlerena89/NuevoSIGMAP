from odoo import api, fields, models, _

class Constructor(models.Model):
    _name = 'nave.constructor'
    _description = _('Constructor')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    es_ecuatoriano = fields.Boolean(
        string=_('is Ecuadorian?'),
        default=True)

    partner_id = fields.Many2one(
        'res.partner',
        string=_('Partner'))

    partner_identification_type_id = fields.Many2one(
        related='partner_id.l10n_latam_identification_type_id',
        string=_('Identification Type'))

    partner_vat = fields.Char(
        related='partner_id.vat',
        string=_('VAT'))

    country_id = fields.Many2one(
        'res.country',
        string=_('Country'),
        required=True,
        tracking=True)

    name = fields.Char(
        string=_('Name'),
        required=True,
        tracking=True)

    puerto_id = fields.Many2one(
        'sigmap.puerto',
        string=_('Port'),
        required=True,
        tracking=True)

    tipo_astillero_id = fields.Many2one(
        'sigmap.tipo.astillero',
        string=_('Shipyard Type'),
        required=True,
        tracking=True)

    nave_ids = fields.One2many(
        'nave.nave.construccion',
        'constructor_id',
        string=_('Ships'))

    @api.onchange('es_ecuatoriano')
    def _onchange_es_ecuatoriano(self):
        self.ensure_one()
        if not self.es_ecuatoriano and self.partner_id:
            if self.partner_id.name == self.name:
                self.name = False
            if self.partner_id.country_id.id == self.country_id:
                self.country_id == False
            self.partner_id = false

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.ensure_one()
        if self.partner_id:
            self.name = self.partner_id.name
            if self.partner_id.country_id:
                self.country_id = self.partner_id.country_id.id
        else:
            self.name = self.country_id = False


class NaveConstruccion(models.Model):
    _name = 'nave.nave.construccion'
    _description = _('Construcción de Naves')

    tipo_construccion_id = fields.Many2one(
        'sigmap.tipo.construccion',
        string=_('Tipo de Construcción'),
        required=True,
        copy=False)

    constructor_id = fields.Many2one(
        'nave.constructor',
        string=_('Constructor'),
        required=True,
        copy=False)

    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Nave'),
        required=False,
        copy=False)

    nave_name = fields.Char(
        string=_('Nombre Nave'),
        required=True,
        copy=False)

    propietario_id = fields.Many2one(
        'sigmap.propietario',
        string=_('Propietario')
    )

    display_type = fields.Selection(
        [
            ('line_section', "Section")
        ],
        default=False,
        help="Technical field for UX purpose.")

    fecha_construccion = fields.Date(
        string=_('Fecha Construcción'),
        required=True,
        copy=False)

    sello_planos_1920 = fields.Image(
        #string=_("Blueprint Registration Number"),
        string=_("Nº Registro - Planos"),
        max_width=1920,
        max_height=1920)
    
    """
    sello_planos_64 = fields.Image(
        string=_("Blueprint Registration Number"),
        related="sello_planos_1920",
        max_width=64,
        max_height=64,
        store=True)
    """

    fecha_planos = fields.Date(
        #string=_('Blueprint Approval Date'))
        string=_('Fecha Aprobación de Planos'))

    fecha_firma_contrato = fields.Date(
        string=_('Fecha Firma Contrato'))

    fecha_puesta_quilla = fields.Date(
        string=_('Fecha Puesta Quilla'))

    active = fields.Boolean(
        string=_('Active?'),
        default=True)


class Nave(models.Model):
    _inherit = 'nave.nave'

    construccion_ids = fields.One2many(
        'nave.nave.construccion',
        'nave_id',
        string=_('Built History'))

    # construccion
    fecha_constr_planos = fields.Date(compute='_compute_fecha_construccion', string='Fecha Aprobación de planos')
    fecha_constr_contrato = fields.Date(compute='_compute_fecha_construccion', string='Fecha Firma de Contrato')
    fecha_constr_quilla = fields.Date(compute='_compute_fecha_construccion', string='Fecha Puesta de Quilla')
    fecha_constr_construccion = fields.Date(compute='_compute_fecha_construccion', string='Fecha construccion')
    planos_constr = fields.Image(compute='_compute_fecha_construccion', string='Planos Construcción')
    # ultima modificación
    fecha_modif_planos = fields.Date(compute='_compute_fecha_construccion', string='Fecha Aprobación de planos')
    fecha_modif_construccion = fields.Date(compute='_compute_fecha_construccion', string='Fecha última modificación')
    planos_modif = fields.Image(compute='_compute_fecha_construccion', string='Planos última modificación')
    
    @api.depends('construccion_ids')
    def _compute_fecha_construccion(self):
        def clean_fields(self):
            field_names = ['fecha_constr_planos', 'fecha_constr_contrato', 'fecha_constr_quilla', 'fecha_constr_construccion', 'planos_constr',
                           'fecha_modif_planos', 'fecha_modif_construccion', 'planos_modif']
            for field_name in field_names:
                self[field_name] = False

        for rec in self:
            clean_fields(rec)
            tipo_contrs_id = self.env.ref("base_sigmap.tipo_construccion_constr").id
            tipo_mofifi_id = self.env.ref("base_sigmap.tipo_construccion_modifi").id
            ultima_modificacion = False
            for construccion in rec.construccion_ids:
                if construccion.tipo_construccion_id.id == tipo_contrs_id:
                    rec.fecha_constr_planos = construccion.fecha_planos
                    rec.fecha_constr_contrato = construccion.fecha_firma_contrato
                    rec.fecha_constr_quilla = construccion.fecha_puesta_quilla
                    rec.fecha_constr_construccion = construccion.fecha_construccion
                    rec.planos_constr = construccion.sello_planos_1920

                if construccion.tipo_construccion_id.id == tipo_mofifi_id and \
                   (not ultima_modificacion or (construccion.fecha_construccion > ultima_modificacion.fecha_construccion)):
                    ultima_modificacion = construccion

            if ultima_modificacion:
                rec.fecha_modif_planos = ultima_modificacion.fecha_planos
                rec.fecha_modif_construccion = ultima_modificacion.fecha_construccion
                rec.planos_modif = ultima_modificacion.sello_planos_1920
