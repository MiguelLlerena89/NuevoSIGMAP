from odoo import api, fields, models, _
import re
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from random import randint

class PersonalMaritimo(models.Model):
    _name = 'personal.maritimo'
    _description = 'Gente de mar'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}
    _rec_names_search = ['name', 'email', 'vat']  # TODO vat must be sanitized the same way for storing/searching

    @property
    def SELF_READABLE_FIELDS(self):
        """ The list of fields a user can read on their own user record.
        In order to add fields, please override this property on model extensions.
        """
        return [
            'signature', 'company_id', 'login', 'email', 'name', 'image_1920',
            'image_1024', 'image_512', 'image_256', 'image_128', 'lang', 'tz',
            'tz_offset', 'groups_id', 'partner_id', '__last_update', 'action_id',
            'avatar_1920', 'avatar_1024', 'avatar_512', 'avatar_256', 'avatar_128',
            'antecedentes_penales', 'fallecido',
            'share',
        ]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """ The list of fields a user can write on their own user record.
        In order to add fields, please override this property on model extensions.
        """
        return ['signature', 'action_id', 'company_id', 'email', 'name', 'image_1920', 'lang', 'tz']


    partner_id = fields.Many2one('res.partner', ondelete='restrict', auto_join=True, index=True,
        string='Persona relacionada', help='Información relacionada a persona de personal marítimo')
    # overridden inherited fields to bypass access rights, in case you have
    # access to the user but not its corresponding partner

    country_of_birth_id = fields.Many2one('res.country', _('Country of Birth'), tracking=True)
    state_of_birth_id = fields.Many2one('res.country.state', _('State of Birth'), domain="[('country_id','=',country_of_birth_id)]",tracking=True)
    city_of_birth_id = fields.Many2one('res.city', _('Place of Birth'),
                                       domain="[('country_id','=',country_of_birth_id), ('state_id','=',state_of_birth_id)]",
                                       tracking=True)
    nationality = fields.Char(related='country_of_birth_id.nationality', string=_('Nationality'), readonly=True, tracking=True)

    birthday = fields.Date(_('Date of Birth'), tracking=True)
    age = fields.Integer(_('Age'), compute="_calcule_age", store=True, readonly=True)
    institutional_email = fields.Char(_('Correo institucional'))

    matricula = fields.Char('Matricula', related="partner_id.vat")
    tipo_personal_mercante = fields.Selection([
        ('tripulante', 'Tripulante'),
        ('oficial', 'Oficial'),
    ], string="Tipo personal mercante", tracking=True)

    genero = fields.Selection([
        ('M', 'MASCULINO'),
        ('F', 'FEMENINO'),
        ('0', 'OTROS')
    ], tracking=True)

    estado_civil = fields.Selection([
        ('soltero', 'Soltero(a)'),
        ('casado', 'Casado(a)'),
        #('cohabitante', 'Cohabitante Legal'),
        ('viudo', 'Viudo(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('union_libre', 'Unión Libre')
    ], string=_('Estado civil'), tracking=True)

    instruccion = fields.Selection([
        ('primaria', 'Primaria'),
        ('ciclo_basico', 'Ciclo Básico'),
        ('bachiller', 'Bachiller'),
        ('tecnico_superior', 'Técnico Superior'),
        ('superior', 'Superior'),
        ('post_grado', _('Post-Grado')),
        ('master', 'Master'),
    ], 'Instrucción', tracking=True)

    parentesco_id = fields.Many2one('res.partner.parentesco', string='Parentesco', tracking=True) #Relationship

    rasgo_particular_ids = fields.One2many('rasgo.particular', 'parent_id', string='Señas Particulares')
    contrato_trabajo_ids = fields.One2many('contrato.trabajo', 'parent_id', string='Contrato Trabajo')

    jerarquia_ids = fields.One2many(
        "personal.maritimo.jerarquia",
        "personal_maritimo_id",
        string="Jerarquía",
        tracking=True,
        context={'active_test': False}
    )
    jerarquia_id = fields.Many2one("personal.maritimo.catalogo.jerarquia", compute="_compute_jerarquia_id", string=_("Jerarquía"), tracking=True)
    #active = fields.Boolean(string=_("Activo odoo?"), default=True, tracking=True)
    dias_disponibles_provisional = fields.Integer(string="Días disponibles para permiso provisional", compute="_compute_permisos_provisionales", default=0, tracking=True)
    dias_disponibles_dispensa = fields.Integer(string="Días disponibles para dispensa", compute="_compute_permisos_provisionales", default=0, tracking=True)
    tipo_trafico = fields.Many2one('tipo.trafico', string='Tipo Trafico', index=True, copy=False, tracking=True)
    tee = fields.Integer(string='Tiempo efectivo de embarque (años)', default=0)

    def _default_clase_persona(self):
        return self.env['personal.maritimo.clase.persona'].browse(self._context.get('clase_persona_id'))

    clase_persona_id = fields.Many2many('personal.maritimo.clase.persona', column1='personal_maritimo_id', column2='clase_persona_id', string='Clase Persona')
    #fallecido = fields.Boolean(related='partner_id.fallecido', store=True)

    tipo_sangre = fields.Selection([
        ('O-', 'O-'),
        ('O+', 'O+'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ], 'Tipo de sangre', index=True, copy=False, tracking=True)

    partner_is_valid = fields.Boolean(
        string=_('Partner is valid?'),
        default=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        computed_value = False
        if self.partner_id:
            partner_vat = self.partner_id.vat
            charterers_for_partner = self.env['personal.maritimo'].search([('partner_id.vat', '=', partner_vat)])
            if len(charterers_for_partner) == 0:
                computed_value = True
            if len(charterers_for_partner) == 1:
                charterer_id = charterers_for_partner[0].id
                if type(self.id) == int:
                    computed_value =  self.id == charterer_id
                else:
                    computed_value = self.id.origin == charterer_id

        self.partner_is_valid = computed_value

    @api.depends('birthday')
    def _calcule_age(self):
        for rec in self:
            if rec.birthday:
                years = relativedelta(date.today(), rec.birthday).years
                months = relativedelta(date.today(), rec.birthday).months
                day = relativedelta(date.today(), rec.birthday).days
                rec.age = int(years)

    def validate_email(self, email):
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
        if match is None:
            raise ValidationError('Correo electrónico inválido.')


    '''
    _sql_constraints = [
        ('vat_uniq', 'unique (vat)',
            'Identificación ya existente!!')
    ]
    '''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            identificacion = vals['vat']
            personal = self.env['personal.maritimo'].search([('vat', '=', identificacion)])
            if personal:
                raise ValidationError(_('Ya existe personal marítimo registrado. %s.', identificacion))
        return super().create(vals_list)


    #@api.onchange('email')
    @api.constrains('email')
    def _check_email(self):
        if self.email:
            self.validate_email(self.email)

    @api.constrains('institutional_email')
    def _check_institutional_email(self):
        if self.institutional_email:
            self.validate_email(self.institutional_email)

    @api.onchange("jerarquia_ids")
    def _compute_jerarquia_id(self):
        # Check for more than one active jerarquia
        for persona in self:
            actives = persona.jerarquia_ids.filtered(lambda c: c.active)
            if len(list(actives)) > 1:
                raise ValidationError('No puede tener más de dos jerarquías activas.')
            elif len(list(actives)) == 1:
                persona.jerarquia_id = actives.jerarquia_id
            else:
                persona.jerarquia_id = False

    @api.onchange("jerarquia_ids")
    def _compute_permisos_provisionales(self):
        # Check for more than one active jerarquia
        for persona in self:
            actives = persona.jerarquia_ids.filtered(lambda c: c.active)
            dias_disponibles_dispensa = persona.dias_disponibles_dispensa
            dias_disponibles_provisional = persona.dias_disponibles_provisional
            if len(list(actives)) > 1:
                raise ValidationError('No puede tener más de una jerarquías activas.')
            elif len(list(actives)) == 1:
                persona.dias_disponibles_dispensa = actives.dias_disponibles_dispensa
                persona.dias_disponibles_provisional = actives.dias_disponibles_provisional
            else:
                persona.dias_disponibles_dispensa = dias_disponibles_dispensa
                persona.dias_disponibles_provisional = dias_disponibles_provisional

    @api.onchange('l10n_latam_identification_type_id')
    def _onchange_l10n_latam_identification_type_id(self):
        for rec in self:
            it_pass = self.env.ref('l10n_latam_base.it_pass', False)
            if rec.l10n_latam_identification_type_id.id != it_pass.id and len(rec.contrato_trabajo_ids)>1:
                rec.contrato_trabajo_ids.unlink()

    def validar_permar(self):
        msg = ''
        if self.partner_id.company_type == 'person':
            if not self.genero:
                msg = msg + 'Género\n'
            if not self.tipo_sangre:
                msg = msg + 'Tipo de sangre\n'
            if not self.estado_civil:
                msg = msg + 'Estado civil\n'
            if not self.birthday:
                msg = msg + 'Fecha de nacimiento\n'
            if not self.country_of_birth_id:
                msg = msg + 'País de nacimiento\n'
            if not self.state_of_birth_id:
                msg = msg + 'Provincia de nacimiento\n'
            if not self.city_of_birth_id:
                msg = msg + 'Lugar de nacimiento\n'
            if not self.nationality:
                msg = msg + 'Nacionalidad\n'
        if msg:
            msg = 'Para la persona %s debe registrar información básica como:\n %s' % (self.name, msg)
            raise ValidationError(_(msg))

    def button_imprimir(self):
        self.validar_permar()
        return self.env.ref('personal_maritimo.action_report_personal_maritimo').report_action(self)

    @api.onchange('first_name', 'last_name')
    def _onchange_concatenate_names(self):
        if self.first_name and self.last_name:
            self.name = f"{self.last_name} {self.first_name}"
        elif self.last_name:
            self.name = self.last_name
        elif self.first_name:
            self.name = self.first_name
        else:
            self.name = ""

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.vat:
                name = '(%s) %s' % (rec.vat, name)
            result.append((rec.id, name))
        return result


class PersonalMaritimoJerarquia(models.Model):
    _name = 'personal.maritimo.jerarquia'
    _description = 'Jerarquía persona'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    personal_maritimo_id = fields.Many2one('personal.maritimo', string='Beneficiario')
    jerarquia_id = fields.Many2one("personal.maritimo.catalogo.jerarquia", string=_("Jerarquía"), tracking=True)
    name = fields.Char(related='jerarquia_id.name')
    curso_id = fields.Many2one("personal.maritimo.curso", string=_("Curso formacion"), tracking=True)
    numero_diploma = fields.Char(related="curso_id.numero_diploma", store=True, readonly=False)
    numero_formulario = fields.Char(related="curso_id.numero_formulario", readonly=False)
    tipo_formacion_id = fields.Many2one(related='curso_id.tipo_formacion_id', string=_("Tipo formacion"), tracking=True, store=True, readonly=False)
    active = fields.Boolean(string=_("Activo?"), default=False, tracking=True)
    folio_acta = fields.Char(string="Folio-Acta")
    dias_disponibles_provisional = fields.Integer(string="Días disponibles para permiso provisional", default=0, tracking=True)
    dias_disponibles_dispensa = fields.Integer(string="Días disponibles para dispensa", default=0, tracking=True)
    tee = fields.Integer(string='Tiempo efectivo de embarque (años)', default=0)
    fecha_ingreso = fields.Date(
        string="Fecha ingreso",
        index=True,
        copy=False,
        tracking=True,
        default=fields.Date.today
    )
    fecha_ascenso = fields.Date(
        string="Fecha ascenso",
        store=True,
        readonly=True,
        index=True,
        copy=False,
        tracking=True,
        compute="_calcular_fechas",
    )
    fecha_deshabilitado = fields.Date(
        string="Fecha deshabilitado",
        compute="_calcular_fechas",
        store=True,
        readonly=True,
        index=True,
        copy=False,
        tracking=True,
    )
    limitacion_id = fields.Many2one("personal.maritimo.catalogo.limitacion", string=_("Limitación"), tracking=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)

    @api.depends('active')
    def _calcular_fechas(self):
        for rec in self:
            if not rec.active:
                rec.fecha_deshabilitado = fields.Date.today()
            else:
                rec.fecha_ascenso = fields.Date.today()

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)


class RasgoParticular(models.Model):
    _name = 'rasgo.particular'
    _description = 'Detalle de señas particulares'
    _order = 'id desc'

    parent_id = fields.Many2one('personal.maritimo', string='Beneficiario')
    particularidad = fields.Selection([
        ('color_piel', 'Color Piel'),
        ('color_cabello', 'Color Cabello'),
        ('color_ojo', 'Color Ojo'),
        ('estatura', 'Estatura'),
        ('peso', 'Peso'),
        ('tatuaje', 'Tatuaje'),
    ], string='Particularidad', tracking=True)
    descripcion = fields.Char('Descripción')
    descripcion_en = fields.Char('Descripción Inglés')

class ContratoTrabajo(models.Model):
    _name = 'contrato.trabajo'
    _description = 'Contrato de trabajo'
    _order = 'id desc'

    parent_id = fields.Many2one('personal.maritimo', string='Beneficiario')
    armador = fields.Many2one('res.partner', string="Armador (Representante Contrato)")
    numero_contrato = fields.Char('No Contrato')
    tipo_visa = fields.Selection([
        ('temporal', 'Visa Temporal'),
        ('permanente', 'Visa Permanente'),
        ('trabajo', 'Visa Trabajo'),
    ], string='Visa', tracking=True)
    fecha_expiracion_visa = fields.Date('Fecha Expiración Visa')
    fecha_inicio = fields.Date('Fecha Inicio Contrato')
    fecha_fin = fields.Date('Fecha Fin Contrato')

class ClasePersona(models.Model):
    _name = 'personal.maritimo.clase.persona'
    _description = 'Clase personal marítimo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Descripcion', required=True)
    active = fields.Boolean(string=_("Activo?"), default=False, tracking=True)

    def name_get(self):
        self.read(['name'])
        return [(rec.id, (rec.name)) for rec in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Clase persona ya exsite!"),
    ]
