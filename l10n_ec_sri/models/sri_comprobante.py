# -*- coding: utf-8 -*-

import os
import hashlib
import secrets
import urllib
import base64
import collections.abc as collections
from xml.sax.saxutils import escape
from io import BytesIO
from . import check_digit
from . import xades_bes
from jinja2 import Environment, FileSystemLoader

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools.config import config

from zeep import Client
from zeep.transports import Transport
from lxml import etree

import logging

_logger = logging.getLogger(__name__)

class SRIComprobante(models.Model):
    _name = "l10n_ec.sri.comprobante"
    _rec_name = "numero"
    _description = 'Comprobantes del SRI'
    _order = 'fecha_emision desc, fecha_autorizacion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    TEMPLATES = {
        '01': 'out_invoice.xml',
    }

    def _default_company(self):
        return self.env.user.company_id

    salt = config.get("salt")
    company_id = fields.Many2one('res.company', string=_('Institución'), default=_default_company)
    partner_id = fields.Many2one('res.partner', string=_('Empresa'))
    sri_autorizacion_id = fields.Many2one('l10n_ec.sri.autorizacion', string=_('Autorización'))
    #sri_pos_documento_id = fields.Many2one('l10n_ec.sri.punto.emision.documento', string=_('Documento punto de emisión'))
    type = fields.Selection([
            ('in','In'),
            ('out','Out'),
        ], string=_('Auth Type'), default='lambda self: self._context.get("auth_type", "out")', index=True)
    is_electronic = fields.Boolean(string=_('Electrónica?'), default=False, index=True)

    fecha_emision = fields.Date(string=_('Fecha Emisión'), index=True)
    tipo_emision = fields.Selection(
        [
            ('1', 'Normal'),
            ('2', 'Indisponibilidad')
        ],
        string='Tipo de Emisión',
        required=True,
        default="1"
    )
    ambiente = fields.Selection(
        [
            ('1', 'Pruebas'),
            ('2', 'Producción')
        ],
        string='Tipo de Ambiente',
        required=True,
        default="1"
    )
    clave_acceso = fields.Char(string=_('Clave Acceso'), size=49, index=True, compute='compute_clave_acceso', store=True, search='search_clave_numero')
    numero_autorizacion = fields.Char(string=_('Número Autorización'), size=49, index=True, compute='compute_clave_acceso', store=True, search='search_clave_numero')
    #sri_ws_id = fields.Many2one('l10n_ec.sri.ws.params', string=_('Parámetros ws'), compute="_compute_sri_params")
    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string=_('Tipo Comprobante'))
    l10n_latam_document_type_code = fields.Char(related='l10n_latam_document_type_id.code', string=_('Tipo comprobante código'))
    establecimiento = fields.Char(string=_('Establecimiento'), size=3, index=True)
    punto_emision = fields.Char(string=_('Punto Emisión'), size=3, index=True)
    secuencial = fields.Char(string=_('Secuencial'), size=9, index=True)
    numero = fields.Char(string=_('Número'), size=15, store=True, compute="compute_numero")
    codigo_numerico = fields.Char(string=_('Código Númerico'), size=8)
    digito_verificador = fields.Char(string=_('Dígito Verificador'), size=1)
    state = fields.Selection([
            ('NEW', 'Pendiente'),
            ('PPR', 'En Procesamiento'),
            ('AUT', 'Autorizado'),
            ('NAT', 'No Autorizado'),
            ('NUL', 'Anulado'),
            ('CONT', 'Contabilizado'),
            ('NCONT', 'No Contabilizado')
        ], string= _('Estado'), default='NEW', index=True)
    state_in = fields.Selection(related='state')
    fecha_autorizacion = fields.Datetime(string=_('Fecha Autorización'))
    error_message = fields.Text(string=_('Mensaje Error'))

    xml_file = fields.Binary(string=_('archivo XML'))
    xml_filename = fields.Char(string=_('nombre archivo'), size=60)

    pdf_file = fields.Binary(string=_('archivo PDF'))
    pdf_filename = fields.Char(string=_('nombre PDF'), size=60)

    def check_configuracion_inicial_empresa(self):
        if not self.company_id.partner_id.vat:
            raise ValidationError(_('No ha configurado el RUC de la compañía'))

        if not self.partner_id.vat:
            raise ValidationError(_('No ha configurado el RUC de la cliente/proveedor seleccionado'))

        if self.is_electronic and self.type in ['out']:
            if not self.company_id.certificate:
                raise ValidationError(_('No ha subido la firma electrónica'))

            if not self.company_id.certificate_password:
                raise ValidationError(_('No ha configurado la contraseña de la firma electrónica'))

    def write(self, vals):
        self.check_configuracion_inicial_empresa()
        return super().write(vals)

    @api.depends('establecimiento', 'punto_emision', 'secuencial')
    def compute_numero(self):
        self.numero = '{0}{1}{2}'.format(
            self.establecimiento,
            self.punto_emision,
            self.secuencial,
        )

    @api.depends('company_id')
    def _compute_sri_params(self):
        sri_ws_id = self.env['l10n_ec.sri.ws.params'].search([('ambiente', '=', self.company_id.ambiente)], limit=1)
        if not sri_ws_id:
            raise ValidationError(_('No hay configurado ningún web service.'))
        else:
            self.sri_ws_id = sri_ws_id.id

    def _get_url_sri_recepcion(self):
        ambiente = self.ambiente
        params = self.env['ir.config_parameter'].sudo()
        if ambiente == '2':
            sri_url_recepcion = params.get_param("l10n_ec_sri.sri_url_recepcion")
        elif ambiente == '1':
            sri_url_recepcion = params.get_param("l10n_ec_sri.sri_url_recepcion_pruebas")
        return sri_url_recepcion

    def _get_url_sri_autorizacion(self):
        ambiente = self.ambiente
        params = self.env['ir.config_parameter'].sudo()
        if ambiente == '2':
            sri_url_autorizacion = params.get_param("l10n_ec_sri.sri_url_autorizacion")
        elif ambiente == '1':
            sri_url_autorizacion = params.get_param("l10n_ec_sri.sri_url_autorizacion_pruebas")
        return sri_url_autorizacion

    def assert_clave_acceso(self, clave_acceso):
        params = self.env['ir.config_parameter'].sudo()
        size = params.get_param("l10n_ec_sri.sri_clave_acceso_size")
        assert len(clave_acceso) == int(size)
        ambiente = clave_acceso[23:24]
        assert ambiente in self.ambiente

    def autorizar(self, comprobante):
        try:
            clave_acceso = etree.fromstring(comprobante).find('infoTributaria').find('claveAcceso').text
        except AttributeError:
            return False
        self.assert_clave_acceso(clave_acceso)

        response = {}
        try:
            client = Client(self._get_url_sri_recepcion(), transport=Transport(timeout=5, operation_timeout=5))
        except Exception as e:
            print(e)
            return 'Error', e
        response = client.service.validarComprobante(comprobante.encode('UTF-8'))

        if 'estado' not in response:
            # TODO raise
            errores = []

        estado = response['estado']

        if estado == 'RECIBIDA':
            errores = []

        elif estado == 'DEVUELTA':
            # Solo fue enviado un comprobante se asumen respuesta para uno solo
            errores = response['comprobantes']['comprobante'][0]['mensajes']['mensaje']

        return estado, errores

    def consultar(self, clave_acceso):
        self.assert_clave_acceso(clave_acceso)

        try:
            client = Client(self._get_url_sri_autorizacion(), transport=Transport(timeout=5, operation_timeout=5))
            response = client.service.autorizacionComprobante(claveAccesoComprobante=clave_acceso)
        except Exception as e:
            print(e)
            return 'Error', e

        if not response['autorizaciones']:
            return False, False

        #return response['autorizaciones']['autorizacion']
        return response['autorizaciones'], False

    def _info_tributaria(self):
        """
        """
        company = self.company_id
        infoTributaria = {
                'ambiente': company.ambiente,
                'tipoEmision': self.tipo_emision,
                'razonSocial': company.name,
                'nombreComercial': company.l10n_ec_business_name,
                'ruc': company.partner_id.vat,
                'claveAcceso': self.clave_acceso,
                'codDoc': self.l10n_latam_document_type_id.code,
                'estab': self.establecimiento,
                'ptoEmi': self.punto_emision,
                'secuencial': self.secuencial.zfill(9),
                'dirMatriz': company.street
                }
        return infoTributaria

    def xml_escape(self, data):
        for key, value in  iter(data.items()):
            if isinstance(value, str):
                data[key] = escape(value)
            elif type(value) == bool and value is False:
                data[key] = ''
            elif isinstance(value, (int, float)):
                pass
            elif isinstance(value, collections.Mapping):
                self.xml_escape(value)
            elif isinstance(value, collections.Iterable):
                for element in value:
                    # List must contain dictionaries
                    if not isinstance(element, collections.Mapping):
                        raise ValidationError('Valor incorrecto para campo %s: %s' % (str(key), str(value)))
                    else:
                        self.xml_escape(element)
            else:
                raise ValidationError('Valor incorrecto para campo %s: %s' % (str(key), str(value)))

    def _info_comprobante(self, comprobante):
        """
        """

        company = comprobante.company_id
        partner = comprobante.partner_id

        infoComprobante = {
            'dirEstablecimiento': company.street2,
            'obligadoContabilidad': 'SI' if company.obligado_contabilidad else 'NO',
            'tipoIdentificacionComprador': partner.l10n_latam_identification_type_id.l10n_ec_sri_code,  # noqa
            'razonSocialComprador': partner.name,
            'identificacionComprador': partner.vat,
        }
        if company.contribuyente_especial:
            if company.resolucion_contribuyente_especial:
                infoComprobante.update({'contribuyenteEspecial':
                                    company.resolucion_contribuyente_especial})
            else:
                raise UserError(_('No ha determinado si es contribuyente especial.'))

        if company.resolucion_agente_retencion:
            resolution = company.resolucion_agente_retencion.split('-')
            infoComprobante.update({'agenteRetencion': resolution[2]})  # noqa

        return infoComprobante

    def _detalles(self, invoice):
        """
        """
        detalles = []
        return {'detalles': detalles}

    def generate_XML(self):
        if not self.clave_acceso or not self.numero_autorizacion:
            self.compute_clave_acceso()
        data = self._info_tributaria()
        func_name =  f'_info_comprobante_{self.l10n_latam_document_type_id.code}'
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            assert callable(func)
            info_comprobante, in_file_path = func()
            data.update(info_comprobante)

            env = Environment(
                loader=FileSystemLoader(os.path.dirname(in_file_path)),
                keep_trailing_newline=True,
            )
            template = env.get_template(os.path.basename(in_file_path))
            self.xml_escape(data)
            edocument = template.render(data)
            edocument = xades_bes.sri_xades_bes(edocument, self.company_id)
            return edocument
        else:
            raise ValidationError(_('El sistema actualmente no soporta este tipo de documento'))

    def action_generate_XML(self):
        self.ensure_one()
        if not self.clave_acceso or not self.numero_autorizacion:
            self.compute_clave_acceso()
        clave_acceso = self.clave_acceso
        if not clave_acceso:
            raise ValidationError(_('No se ha podido generar la clave de acceso'))

        edocument = self.generate_XML()

        xmlfile = BytesIO()
        xmlfile.write(edocument.encode('utf-8'))

        self.write({
            'xml_file': base64.encodebytes(xmlfile.getvalue()),
            'xml_filename': clave_acceso + '.xml',
        })
        xmlfile.close()

        attachment = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('res_field', '=', 'xml_file')
        ])

        if attachment:
            attachment.sudo().mimetype = 'application/xml'

        return attachment

    def action_auth_XML(self):
        for obj in self:
            if self.state in ['AUT', 'ANU', 'NAT']:
                return

            obj.action_generate_XML()
            file_raw = obj.xml_file
            estado, errores = self.autorizar(base64.decodebytes(file_raw).decode('utf-8'))
            if estado == 'RECIBIDA':
                obj.state = 'PPR'
                resultado = self.consultar(obj.clave_acceso)
                auth = resultado['autorizacion'][0]
                if resultado:
                    fecha_autorizacion = auth['fechaAutorizacion']
                    estado = auth['estado']
                    if estado == 'AUTORIZADO':
                        obj.state = 'AUT'
                        obj.fecha_autorizacion = fecha_autorizacion.replace(tzinfo=None)
                        obj.send_authorized_document_mail()
            message = """
                ESTADO DE DOCUMENTO ELECTRÓNICO: %s <br><br>
                CLAVE DE ACCESO: %s <br>
                NÚMERO DE AUTORIZACIÓN %s <br>
                FECHA AUTORIZACIÓN: %s <br>
                AMBIENTE: %s <br>
            """ % (
                estado,
                obj.clave_acceso,
                obj.numero_autorizacion,
                obj.fecha_autorizacion,
                obj.ambiente
            )
            if errores:
                message += """
                    ERROR: %s <br><br>
                """ % (
                    errores,
                )
            obj.message_post(body=message)

    def action_check_auth(self):
        for obj in self:
            resultado = self.consultar(obj.clave_acceso)
            if not resultado:
                raise ValidationError(_('No hay información de este documento'))
            if 'autorizacion' in resultado:
                auth = resultado['autorizacion'][0]
                if 'fechaAutorizacion' in auth:
                    fecha_autorizacion = auth['fechaAutorizacion']
                else:
                    fecha_autorizacion = False
                if 'estado' in auth:
                    message = ""
                    if auth['estado'] == 'AUTORIZADO':
                        obj.state = 'AUT'
                        obj.fecha_autorizacion = fecha_autorizacion.replace(tzinfo=None)
                        message = """
                            ESTADO DE DOCUMENTO ELECTRÓNICO: %s <br><br>
                            CLAVE DE ACCESO: %s <br>
                            NÚMERO DE AUTORIZACIÓN %s <br>
                            FECHA AUTORIZACIÓN: %s <br>
                            AMBIENTE: %s <br>
                        """ % (
                            auth['estado'],
                            obj.clave_acceso,
                            obj.numero_autorizacion,
                            obj.fecha_autorizacion,
                            obj.ambiente
                        )
                    if auth['estado'] == 'NO AUTORIZADO':
                        mensaje = False
                        if 'mensajes' in auth:
                            if 'mensaje' in auth['mensajes']:
                                mensaje = auth['mensajes']['mensaje'][0]
                        if 'tipo' in mensaje:
                            if mensaje['tipo'] == 'ERROR':
                                obj.state = 'NAT'
                            message = """
                                ESTADO DE DOCUMENTO ELECTRÓNICO: %s <br><br>
                                MENSAJE: %s %s
                                CLAVE DE ACCESO: %s <br>
                                NÚMERO DE AUTORIZACIÓN %s <br>
                                AMBIENTE: %s <br>
                                INFORMACIÓN_ADICIONAL: %s
                            """ % (
                                auth['estado'],
                                mensaje['tipo'],
                                mensaje['mensaje'],
                                obj.clave_acceso,
                                obj.numero_autorizacion,
                                obj.ambiente,
                                mensaje['informacionAdicional']
                            )
                    obj.message_post(body=message)

    @api.depends('is_electronic', 'sri_autorizacion_id', 'partner_id', 'company_id')
    def compute_clave_acceso(self):
        """ Calcular clave de acceso y numero de Autorizacion
        Comprobantes FISICOS
            Es el mismo procedimiento para comprobantes EMITIDOS y RECIBIDOS
            - Clave de acceso: No hay clave de acceso para comprobantes fisicos -> False
            - Numero de Autorizacion: Se toma el valor del campo "numero" de la autorizacion
              "sri_autorizacion_id (sri.autorizacion)"
        Comprobantes ELECTRONICOS
            EMITIDOS
                Se utiliza el modo OFFLINE, por lo que el numero de autorizacion es la clave de acceso
                - Los valores de los campos "codigo_numerico" y "digito_verificador" son calculados
                  en conjunto con la clave de acceso y el numero de Autorizacion
            RECIBIDOS
                TODO: Cambios para el modo ONLINE, clave de acceso es calculada, pero numero de
                      autorizacion no, este se recibe del SRI
                - Para generar el mismo numero que viene en el comprobante, se guardan los campos
                  "codigo_numerico" y "digito_verificador" para con estos se puedan calcular la
                  clave de acceso y numero de Autorizacion
        """
        for comprobante in self:
            if not comprobante.type.startswith('in'):
                comprobante.clave_acceso = ''
                comprobante.numero_autorizacion = ''
                if not comprobante.is_electronic:
                    # EMITIDOS Y RECIBIDOS FISICOS
                    if comprobante.sri_autorizacion_id:
                        comprobante.numero_autorizacion = comprobante.sri_autorizacion_id.numero
                else:
                    # ELECTRONICOS
                    try:
                        fecha_emision = comprobante.fecha_emision.strftime('%d%m%Y')
                        tipo_comprobante = comprobante.l10n_latam_document_type_id.code
                        ruc = comprobante.partner_id.vat if not comprobante.type.startswith('out') else\
                            comprobante.company_id.partner_id.vat
                        tipo_emision = comprobante.tipo_emision if not comprobante.type.startswith('out')\
                            else comprobante.company_id.tipo_emision
                        ambiente = comprobante.ambiente if not comprobante.type.startswith('out') else\
                            comprobante.company_id.ambiente
                        codigo_numerico = comprobante.codigo_numerico if not\
                            comprobante.type.startswith('out') else self.get_codigo_numerico()

                        access_key_prev = [fecha_emision, tipo_comprobante, ruc, ambiente,
                            comprobante.numero, codigo_numerico, tipo_emision]
                        access_key_prev = ''.join(access_key_prev)

                        digito_verificador = comprobante.digito_verificador\
                            if not comprobante.type.startswith('out') else\
                            check_digit.CheckDigit.compute_mod11(access_key_prev)

                        clave_acceso = ''.join([access_key_prev, str(digito_verificador)])
                        comprobante.clave_acceso = clave_acceso
                        comprobante.numero_autorizacion = clave_acceso
                    except Exception as e:
                        _logger.exception('Error while computed clave acceso in %s()',
                            'compute_clave_acceso')
                        print(e)

    def search_clave_numero(self, value):
        domain_to_search = []
        if not self.is_electronic:
            sri_autorisation_ids = self.env['l10n_ec.sri.autorizacion'].search([('numero', '=', value)]).mapped('id')
            domain_to_search = [('is_electronic', '=', False), ('sri_authorisation_id', 'in', sri_autorisation_ids)]
        else:
            try:
                try_domain = []
                identificacion = value[10:23]
                partner_id = self.env['res.partner'].search([('vat', '=', identificacion)])
                if len(partner_id) == 1:
                    try_domain.append(('is_electronic', '=', True))
                    try_domain.append(('fecha_emision', '=', value[:8]))
                    try_domain.append(('tipo_comprobante', '=', value[8:10]))
                    try_domain.append(('partner_id', '=', partner_id.id))
                    try_domain.append(('ambiente', '=', value[23:24]))
                    try_domain.append(('establecimiento', '=', value[24:27]))
                    try_domain.append(('punto_emision', '=', value[27:30]))
                    try_domain.append(('secuencial', '=', value[30:39]))
                    try_domain.append(('codigo_numerico', '=', value[39:47]))
                    try_domain.append(('', '=', value[47:48]))
                    try_domain.append(('digito_verificador', '=', value[48:49]))
            except Exception as e:
                print(e)
                try_domain = []
            else:
                domain_to_search = try_domain
        return domain_to_search

    def get_codigo_numerico(self):
        if not self.salt:
            raise ValidationError(_('Contacte al administrador'))

        if self.numero:
            codigo_numerico = str(int(hashlib.pbkdf2_hmac(
                    'sha256',
                    self.numero.encode(),
                    self.salt.encode(),
                    1000
                ).hex(), 16) % (10 ** 8)
            ).zfill(8)
            return codigo_numerico
        else:
            raise ValidationError(_('No existe número de comprobante'))


    def send_authorized_document_mail(self):
        self.ensure_one()
        try:
            template_id = self.env.ref('l10n_ec_sri.email_template_comprobante', raise_if_not_found=False)
            data = []
            if self.is_electronic:
                func_name =  f'_get_report_data_{self.l10n_latam_document_type_id.code}'
                if hasattr(self, func_name):
                    func = getattr(self, func_name)
                    assert callable(func)
                    report_ref, report_id = func()

                    data_pdf_id = self.attachment_PDF(report_ref, report_id)
                    if data_pdf_id:
                        data.append(data_pdf_id.id)

                    data_xml_id = self.action_generate_XML()
                    if data_xml_id:
                       data.append(data_xml_id.id)
                email_template = self.env['mail.template'].browse(template_id.id)
                email_template.sudo().attachment_ids = [(6, 0, data)]
                email_template.send_mail(self.id, raise_exception=False, force_send=True)

        except Exception as e:
            _logger.error('Error : %s ' % e)
            raise ValidationError(_('Hubo un error en envío del documento autorizado'))


    def action_send_email(self):
        self.ensure_one()
        try:
            template_id = self.env.ref('l10n_ec_sri.email_template_comprobante', raise_if_not_found=False)
            data = []
            if self.is_electronic:
                func_name =  f'_get_report_data_{self.l10n_latam_document_type_id.code}'
                if hasattr(self, func_name):
                    func = getattr(self, func_name)
                    assert callable(func)
                    report_ref, report_id = func()

                    data_pdf_id = self.attachment_PDF(report_ref, report_id)
                    if data_pdf_id:
                        data.append(data_pdf_id.id)

                    data_xml_id = self.action_generate_XML()
                    if data_xml_id:
                        data.append(data_xml_id.id)

                    if data:
                        template_id.write({'attachment_ids': [(6, 0, data)]})
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form', raise_if_not_found=False)
            ctx = dict(self.env.context or {})
            ctx.update({
                'default_model': 'l10n_ec.sri.comprobante',
                'active_model': 'l10n_ec.sri.comprobante',
                'active_id': self.ids[0],
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id.id,
                'default_composition_mode': 'comment',
                'custom_layout': False, #revisar notificacion
                'force_email': True,
                'mark_so_as_sent': True,
                'model_description': self.l10n_latam_document_type_id.name,
            })

            return {
                'name': _('Compose Email'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id.id, 'form')],
                'view_id': compose_form_id.id,
                'target': 'new',
                'context': ctx,
            }

        except Exception as e:
            _logger.error('Error : %s ' % e)
            raise ValidationError(_('Hubo un error en envío de correo.'))


    def attachment_PDF(self, report_ref, report_id):
        for obj in self:
            if not obj.clave_acceso or not obj.numero_autorizacion:
                obj.compute_clave_acceso()
            clave_acceso = obj.clave_acceso
            emission_code = obj.env.user.company_id.tipo_emision

            #pdf_bin = self.env.ref(report_ref)._render_qweb_pdf(report_id)[0]
            pdf_bin = self.env['ir.actions.report']._render_qweb_pdf(report_ref, report_id)[0]
            context_out = base64.b64encode(pdf_bin)

            attachment_name = clave_acceso if clave_acceso else obj.numero_autorizacion
            filename = "%s.%s" % (attachment_name, "pdf")

            self.write({
                'pdf_file': context_out,
                'pdf_filename': filename,
            })

            attachment_id = self.env['ir.attachment'].create({
                'name': filename,
                'datas': context_out,
                # 'mimetype': 'application/x-pdf',
                # 'res_field': 'pdf_file',
                'res_model': self._name,
                'res_id': self.id,
                'type': 'binary',
            })

            return attachment_id
