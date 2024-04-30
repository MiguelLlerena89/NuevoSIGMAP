from odoo import api, fields, models, _
import re
from odoo.exceptions import ValidationError, UserError, AccessError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from random import randint
from . import utils

from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep import helpers
from zeep.transports import Transport
import logging.config

from odoo.tools.config import config

def verify_final_consumer(vat):
    return vat == '9' * 13  # final consumer is identified with 9999999999999


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(
        string=_('Company Type'),
        selection=[
            ('person', _('Individual')),
            ('company', _('Company'))
        ],
        compute='_compute_company_type',
        inverse='_write_company_type')

    tipo_juridica = fields.Selection(
        string=_('Company Nature'),
        selection=[
            ('publica', _('Public')),
            ('privada', _('Private'))
        ],
        compute='_compute_tipo_juridica',
        required=False,
        readonly=False,
        index=True,
        default=False,
        tracking=True)

    birthday = fields.Date(
        string=_('Date of Birth'),
        copy=False,
        tracking=True)

    genero = fields.Selection([
            ('M', _('Male')),
            ('F', _('Female')),
            ('0', _('Other'))
        ],
        string=_('Gender'),
        default=False,
        tracking=True)

    estado_civil = fields.Selection([
            ('soltero', _('Single')),
            ('casado', _('Married')),
            ('viudo', _('Widower')),
            ('divorciado', _('Divorced')),
            ('union_libre', _('Free Union'))
        ],
        string=_('Marital Status'),
        tracking=True)

    country_id = fields.Many2one(default=lambda self: self.env.ref('base.ec', raise_if_not_found=False))

    parentesco_id = fields.Many2one('personal.maritimo.parentesco', string='Parentesco', tracking=True) #Relationship

    image_firma = fields.Image('Imagen de firma')
    es_activo = fields.Boolean(string=_("Activo?"), default=True, tracking=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)
    fallecido = fields.Boolean(string=_("Fallecido?"), compute="_compute_check_fallecido", tracking=True, store=True)
    discapacidad = fields.Boolean(string=_("Discapacidad?"), compute="_compute_check_fallecido", tracking=True)
    porcentaje_discapacidad = fields.Char(string=_("Porcentaje discapacidad?"), compute="_compute_check_fallecido", tracking=True)
    tipo_discapacidad = fields.Char(string=_("Tipo discapacidad?"), compute="_compute_check_fallecido", tracking=True)
    age = fields.Integer(_('Age'), compute="_calcule_age", store=True, readonly=True)
    fecha_defuncion = fields.Date(
        string=_('Fecha defunción'),
        copy=False,
        tracking=True)

    aplica_descuento = fields.Boolean(_('Aplica descuento?'), compute="_compute_check_discount")
    antecedentes_penales = fields.Boolean(_('Tiene antecedentes penales?'), compute="_compute_check_antecedentes_penales")

    first_name = fields.Char(string=_('First Name'), tracking=True)
    last_name = fields.Char(string=_('Last Name'), tracking=True)

    @api.depends('birthday')
    def _calcule_age(self):
        for rec in self:
            if rec.birthday:
                years = relativedelta(date.today(), rec.birthday).years
                months = relativedelta(date.today(), rec.birthday).months
                day = relativedelta(date.today(), rec.birthday).days
                rec.age = int(years)

    @api.depends('age', 'discapacidad')
    def _compute_check_discount(self):
        for rec in self:
            if rec.age >= 65 or rec.discapacidad:
                rec.aplica_descuento = True
            else:
                rec.aplica_descuento = False

    def _get_url_dinarp(self):
        params = self.env['ir.config_parameter'].sudo()
        url = params.get_param("base_sigmap.dinarp_url")
        if url:
            return url
        return False

    def _get_conexion(self):
        session = Session()
        client = False
        url = self._get_url_dinarp()
        dinarp_user = config.get("dinarp_user")
        dinarp_password = config.get("dinarp_passwd")
        session.auth = HTTPBasicAuth(dinarp_user, dinarp_password)

        if not url:
            raise ValidationError('No se ha configurado URL. Agreguela en la configuración')

        try:
            client = Client(url, transport=Transport(session=session, timeout=2, operation_timeout=3))
        except Exception as e:
            print('Error', e)
        return client

    def _get_data_registro_civil(self, vat):
        client = self._get_conexion()

        if not client:
            return False
        parametro = client.get_type('ns0:parametro')
        parametros = client.get_type('ns0:parametros')

        obj = parametro(nombre="codigoPaquete", valor="4997")
        obj2 = parametro(nombre="identificacion", valor=vat)

        result = False

        try:
            result = client.service.consultar(parametros([obj, obj2]))
        except Exception as e:
            print(e)

        if not result:
            return False

        data = {}
        for clave, valores in helpers.serialize_object(result)['entidades'].items():
            for valor in valores:
                for valor_fila, fila in valor['filas'].items():
                    for columnas in fila:
                        for clave_col, columna in columnas['columnas'].items():
                            for detalle_col in columna:
                                if 'estadoCivil' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'estadoCivil': detalle_col['valor']
                                    })
                                if 'sexo' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'sexo': detalle_col['valor']
                                    })
                                if 'fechaNacimiento' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'fechaNacimiento': detalle_col['valor']
                                    })
                                if 'estadoCivil' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'estadoCivil': detalle_col['valor']
                                    })
                                if 'callesDomicilio' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'callesDomicilio': detalle_col['valor']
                                    })
                                if 'fechaDefuncion' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'fechaDefuncion': detalle_col['valor']
                                    })

                                if 'tipoDiscapacidad' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'tipoDiscapacidad': detalle_col['valor']
                                    })

                                    if 'porcentajeDiscapacidad' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                        data.update({
                                            'porcentajeDiscapacidad': detalle_col['valor']
                                        })
        return data

    def _get_data_sri(self, vat):

        client = self._get_conexion()

        if not client:
            return False

        parametro = client.get_type('ns0:parametro')
        parametros = client.get_type('ns0:parametros')

        obj = parametro(nombre="codigoPaquete", valor="4999")
        obj2 = parametro(nombre="identificacion", valor=vat)
        obj3 = parametro(nombre="fuenteDatos", valor='')

        result = client.service.consultar(parametros([obj, obj2, obj3]))
        if not result:
            return False

        data = {}
        for clave, valores in helpers.serialize_object(result)['entidades'].items():
        #for clave, valores in result['entidades'].items()
            print(clave, valores)
            # persona juridica coincida con lo que está en el SRI
        return data

    @api.depends("vat", "l10n_latam_identification_type_id")
    def _compute_check_info_sri(self):
        for partner in self:
            if partner.vat and self.env.ref("l10n_ec.ec_ruc", False) == partner.l10n_latam_identification_type_id:
                data = self._get_data_sri(partner.vat)

    @api.depends("vat", "country_id", "l10n_latam_identification_type_id")
    def _compute_check_antecedentes_penales(self):
        for partner in self:
            if self.antecedentes_penales:
                return
            partner.antecedentes_penales = False
            if partner.vat and self.env.ref("l10n_ec.ec_dni", False) == partner.l10n_latam_identification_type_id:
                data = utils._get_data_antecedentes_penales(partner.vat)
                if data:
                    partner.antecedentes_penales = True
                    #Agregar cuadrado en rojo que tiene antecedentes penales

    @api.depends("vat", "country_id", "l10n_latam_identification_type_id")
    def _compute_check_fallecido(self):
        for partner in self:
            partner.discapacidad = False
            partner.porcentaje_discapacidad = False
            partner.tipo_discapacidad = False
            if partner.fallecido:
                return
            partner.fallecido = False
            partner.fecha_defuncion = False
            if partner.vat and self.env.ref("l10n_ec.ec_dni", False) == partner.l10n_latam_identification_type_id:
                data = self._get_data_registro_civil(partner.vat)
                if not data:
                    return
                if 'fechaDefuncion' in data:
                    if data['fechaDefuncion']:
                        partner.fallecido = True
                        partner.fecha_defuncion = datetime.strptime(data['fechaDefuncion'], '%d/%m/%Y')
                        partner.action_archive()
                if 'tipoDiscapacidad' in data and 'porcentajeDiscapacidad' in data:
                    if data['tipoDiscapacidad']:
                        partner.discapacidad = True
                        partner.tipo_discapacidad = data['tipoDiscapacidad']
                        partner.porcentaje_discapacidad = data['porcentajeDiscapacidad']

    @api.depends("vat", "country_id", "l10n_latam_identification_type_id")
    def _compute_l10n_ec_vat_validation(self):
        it_ruc = self.env.ref("l10n_ec.ec_ruc", False)
        it_dni = self.env.ref("l10n_ec.ec_dni", False)
        for partner in self:
            partner.l10n_ec_vat_validation = False
            if partner and partner.l10n_latam_identification_type_id in (it_ruc, it_dni) and partner.vat:
                final_consumer = verify_final_consumer(partner.vat)
                if not final_consumer:
                    partner.l10n_ec_vat_validation = False


    '''
    #   Field tipo_juridica as a computed value
    #
    #    tipo_juridica = fields.Selection(
    #    string='Tipo Sociedad',
    #    selection=[
    #        ('publica', 'Pública'),
    #        ('privada', 'Privada')],
    #    compute='_compute_tipo_juridica',
    #    required=False,
    #    readonly=False)

    @api.depends('company_type', 'l10n_latam_identification_type_id', 'vat')
    def _compute_tipo_juridica(self):
        for partner in self:
            try:
                ruc = self.env.ref('l10n_ec.ec_ruc', False)
                if ruc and partner.company_type == 'company' and partner.l10n_latam_identification_type_id == ruc and partner.vat:
                    if len(partner.vat) == 13:
                        if partner.vat[2] == '6':
                            partner.tipo_juridica = 'publica'
                        if partner.vat[2] == '9':
                            partner.tipo_juridica = 'privada'
                    else:
                        raise ValidationError('Identificación de la persona inválida.')
                else:
                    partner.tipo_juridica = False
            except AccessError:
                partner.tipo_juridica = False
    '''

    @api.depends('company_type', 'l10n_latam_identification_type_id', 'vat')
    def _compute_tipo_juridica(self):
        for partner in self:
            partner.tipo_juridica = False
            ruc = self.env.ref('l10n_ec.ec_ruc', False)
            if ruc and partner.company_type == 'company' and partner.l10n_latam_identification_type_id == ruc and partner.vat:
                if len(partner.vat) == 13:
                    if partner.vat[2] == '6':
                        partner.tipo_juridica = 'publica'
                    if partner.vat[2] == '9':
                        partner.tipo_juridica = 'privada'

    @api.onchange('vat')
    def _onchange_check_data(self):
        if self.vat and self.env.ref("l10n_ec.ec_dni", False) == self.l10n_latam_identification_type_id:
            data = self._get_data_registro_civil(self.vat)
            if not data:
                return
            if 'fechaNacimiento' in data:
                if data['fechaNacimiento']:
                    fecha_nacimiento = datetime.strptime(data['fechaNacimiento'], '%d/%m/%Y')
                    if fecha_nacimiento != self.birthday:
                        self.birthday = fecha_nacimiento
            if 'sexo' in data:
                sexo = data['sexo']
                genero = {
                    'HOMBRE': 'M',
                    'MUJER': 'F'
                }
                if sexo:
                    if sexo in genero:
                        self.genero = genero[sexo]
                    else:
                        print(sexo)
            if 'estadoCivil' in data:
                estado_civil = data['estadoCivil']
                if estado_civil:
                    self.estado_civil = estado_civil.lower()
            if 'callesDomicilio' in data:
                direccion = data['callesDomicilio']
                if direccion:
                    if not self.street:
                        self.street = direccion
                    print(self.street)

    @api.onchange('first_name', 'last_name')
    def _onchange_concatenate_names(self):
        if self.last_name and self.first_name:
            self.name = f"{self.last_name} {self.first_name}"
        elif self.last_name:
            self.name = self.last_name
        elif self.first_name:
            self.name = self.first_name
        else:
            self.name = ""