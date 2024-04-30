from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EmpresaMantenimientoTipo(models.Model):
    _name = 'nave.empresa.mantenimiento.tipo'
    _description = 'Empresa Mantenimiento - Tipo'
    _order = 'name'

    name = fields.Char(string=_('Nombre'))
    active = fields.Boolean(_('active'), default=True)


class EmpresaMantenimientoClasificacion(models.Model):
    _name = 'nave.empresa.mantenimiento.clasificacion'
    _description = 'Empresa Mantenimiento - Clasificación'
    _order = 'name'

    name = fields.Char(string=_('Nombre'))
    active = fields.Boolean(_('active'), default=True)


class EmpresaMantenimientoUso(models.Model):
    _name = 'nave.empresa.mantenimiento.uso'
    _description = 'Empresa Mantenimiento - Uso'
    _order = 'name'

    name = fields.Char(string=_('Nombre'))
    active = fields.Boolean(_('active'), default=True)


class EmpresaMantenimiento(models.Model):
    _name = 'nave.empresa.mantenimiento'
    _rec_name = 'partner_id'
    _description = 'Empresa Mantenimiento'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}

    active = fields.Boolean(_('active'), default=True)

    partner_id = fields.Many2one(
        'res.partner',
        string=_('Empresa/Persona'))

    tipo_id = fields.Many2one(
        'nave.empresa.mantenimiento.tipo',
        index=True,
        required=True,
        string=_('Tipo Servicio'))

    jurisdiccion_id = fields.Many2one(
        'sigmap.jurisdiccion',
        index=True,
        required=True,
        string=_('Jurisdicción'))

    """
    partner_identification_type_id = fields.Many2one(
        related='partner_id.l10n_latam_identification_type_id',
        string=_('Identification Type'))

    partner_vat = fields.Char(
        related='partner_id.vat',
        string=_('VAT'))

    partner_company_type = fields.Selection(
        related='partner_id.company_type',
        string=_('Tipo Compañía'))

    partner_business_name = fields.Char(
        related='partner_id.l10n_ec_business_name',
        string=_('Nombre Comercial'))

    partner_representante_legal = fields.Many2one(
        related='partner_id.representante_legal_id',
        string=_('Representante Legal'))
    """
    direccion = fields.Char(
        index=False,
        required=False,
        string=_('Direccion'))


    clasificacion_id = fields.Many2one(
        'nave.empresa.mantenimiento.clasificacion',
        index=True,
        required=False,
        string=_('Clasificación'))

    uso_id = fields.Many2one(
        'nave.empresa.mantenimiento.uso',
        index=True,
        required=False,
        string=_('Uso'))

    guias_longitud = fields.Integer(
        index=False,
        required=False,
        string=_('Longitud Guías (M)'))
    guias_numero = fields.Integer(
        index=False,
        required=False,
        string=_('Número Guías'))

    capacidad_levante = fields.Float(
        index=False,
        required=False,
        string=_('Capacidad Levante (Tn)'))
    potencia_winche = fields.Float(
        index=False,
        required=False,
        string=_('Potencia Winche (HP)'))

    area_ocupacion = fields.Float(
        index=False,
        required=False,
        string=_('Área de Ocupación (m2)'))

    acuerdo_ministerial = fields.Char(
        index=True,
        required=False,
        string=_('Acuerdo Ministerial'))
    
    representante_tecnico_id = fields.Many2one(
        'res.partner',
        index=True,
        required=False,
        string=_('Representante Técnico'))

    observacion = fields.Text(
        index=False,
        required=False,
        string=_('Observación'))

    partner_is_valid = fields.Boolean(
        string=_('Empresa es válida?'),
        default=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        computed_value = False
        if self.partner_id:
            partner_vat = self.partner_id.vat
            empresas_for_partner = self.env['nave.empresa.mantenimiento'].search([('partner_id.vat', '=', partner_vat)])
            if len(empresas_for_partner) == 0:
                computed_value = True
            if len(empresas_for_partner) > 1:
                computed_value = False
            if len(empresas_for_partner) == 1:
                empresa_id = empresas_for_partner[0].id
                if type(self.id) == int:
                    computed_value =  self.id == empresa_id
                else:
                    computed_value = self.id.origin == empresa_id

        self.partner_is_valid = computed_value



class AutorizaciónEmpresaMantenimiento(models.Model):
    _name = 'nave.autorizacion.empresa.mantenimiento'
    _description = _('Relación entre la Empresa de Mantenimiento y sus autorizaciones')
    _inherits = {'sigmap.owner.matricula': 'owner_matricula_id'}
    _order = 'fecha_caducidad desc'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    owner_matricula_id = fields.Many2one(
        'sigmap.owner.matricula',
        ondelete='restrict',
        auto_join=True,
        copy=False,
        string=_('Autorización relacionada a la empresa de Mantenimiento'))
    # overridden inherited fields to bypass access rights, in case you have
    # access to the user but not its corresponding partner

    empresa_mantenimiento_id = fields.Many2one(
        'nave.empresa.mantenimiento',
        ondelete='restrict',
        copy=False,
        string=_('Empresa de Mantenimiento'),
        help=_('Empresa de Mantenimiento registrada en la autorización'))
    
    is_canceled = fields.Boolean(
        string=_('Anulada?'),
        default=False)



class EmpresaMantenimiento(models.Model):
    _inherit = 'nave.empresa.mantenimiento'

    autorizacion_ids = fields.One2many(
        string=_('Autorizaciones'),
        comodel_name='nave.autorizacion.empresa.mantenimiento',
        inverse_name='empresa_mantenimiento_id')

    matricula = fields.Char(
        compute='_compute_matricula',
        string=_('Código'))
    
    matricula_caducidad = fields.Char(
        compute='_compute_matricula',
        string=_('Caduca en'))

    matricula_active = fields.Boolean(
        compute='_compute_matricula',
        string=_('Activa?'))

    matricula_estado = fields.Char(
        compute='_compute_matricula',
        string=_('Estado?'))

    @api.depends('autorizacion_ids')
    def _compute_matricula(self):
        for rec in self:
            rec.matricula = ''
            rec.matricula_caducidad = ''
            rec.matricula_active = False
            rec.matricula_estado = ''

            if rec.autorizacion_ids:
                current_matricula = [ reg_num for reg_num in rec.autorizacion_ids if reg_num['active'] and not reg_num['is_canceled'] ]
                if len(current_matricula) == 1:
                    rec.matricula = current_matricula[0]['codigo_documento']
                    rec.matricula_caducidad = current_matricula[0]['fecha_caducidad']
                    rec.matricula_active = True
                    rec.matricula_estado = _('Vigente')
                elif len(current_matricula) == 0:
                    active_matriculas = [ reg_num for reg_num in rec.autorizacion_ids if reg_num['active'] ]
                    if len(active_matriculas) > 0:
                        rec.matricula_active = True
                        rec.matricula_estado = _('Anulada/Suspendida')
                        rec.matricula_caducidad = active_matriculas[0]['fecha_caducidad']
                elif len(current_matricula) < len(rec.autorizacion_ids):
                    rec.matricula_active = _('Caducada')
