import base64
import json
import subprocess

from asn1crypto import cms
import dateutil

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ActaConfidencialidad(models.Model):
    _name = 'acta.confidencialidad'
    _description = 'Acta confidencialidad'

    user_id = fields.Many2one('res.users', string='Usuario', required=True, readonly=True)

    # Defined again in module usuarios_documentos, inherit tramite.documento.firma
    elabora_id = fields.Many2one("res.users", string=_("Elaborado por"), readonly=True, tracking=True,
                                 default=lambda self: self.env.user)
    supervisa_id = fields.Many2one("res.users", string=_("Supervisado por"), readonly=True, tracking=True)
    aprueba_id = fields.Many2one("res.users", string=_("Aprobado por"), readonly=True, tracking=True)
    reparto_id = fields.Many2one('sigmap.reparto', readonly=True)

    oficio_ids = fields.One2many('acta.confidencialidad.oficio', 'acta_confidencialidad_id', string='Oficios')

    es_externo = fields.Boolean('Externo', readonly=True)

    departamento_id = fields.Many2one('sigmap.departamento', readonly=True)
    cargo_id = fields.Many2one('sigmap.cargo', readonly=True)
    rango_id = fields.Many2one('tipo.rango', string='Grado')
    especialidad_id = fields.Many2one('sigmap.especialidad', readonly=True)
    profesion_abreviatura = fields.Char('Profesión abreviatura', related='user_id.profesion_abreviatura', store=True)

    entidad_externa_id = fields.Many2one('sigmap.entidad.externa', readonly=True)

    active = fields.Boolean(_('Active?'), default=True)

    state = fields.Selection([
        ('por_supervisar', 'Por supervisar'),
        ('por_firmar', 'Por Aprobar'),
        ('vigente', 'Vigente'),
        ('usuario_activado', 'Usuario activado'),
        ('anulado', 'Anulado'),
    ], string='Estado', default='por_supervisar', index=True, copy=False, tracking=True)
    archivo_firmado = fields.Binary('Archivo firmado', tracking=True, copy=False)
    archivo_firmado_filename = fields.Char(string='Nombre archivo firmado', tracking=True, copy=False)

    archivo_firmado_por_usuario = fields.Binary('Archivo firmado por usuario', tracking=True, copy=False)
    archivo_firmado_por_usuario_filename = fields.Char(string='Nombre archivo firmado por usuario', tracking=True, copy=False)
    es_firma_valida = fields.Boolean(_('Firma de usuaario válida?'), default=False, readonly=True)

    firmas_ids = fields.One2many('acta.confidencialidad.firma', 'acta_confidencialidad_id', string='Firmas',
                                 compute='_compute_firmas', store=True)

    def _get_texto(self):
        params = self.env['ir.config_parameter'].sudo()

        hidden_categories = [
            'base.module_category_hidden',
            'base.module_category_sales_sales',
            'base.module_category_accounting_accounting',
            'base.module_category_usability',
            'base.module_category_user_type'
        ]

        groups = ''.join([f'<li>{g.name}</li>' for g in self.user_id.groups_id
                          if g.category_id.xml_id not in hidden_categories])

        texto = params.get_param("usuarios.acta_confidencialidad_texto")

        if isinstance(texto, str):
            return texto.replace('{ROLES}', f'<ul>{groups}</ul>')

        return texto

    def action_supervisar(self):
        return super().action_supervisar()

    def action_aprobar(self):
        return super().action_aprobar()

    def action_activar_usuario(self):
        if not self.es_firma_valida:
            raise ValidationError("Debe tener firma válida")

        self.write({"state": "usuario_activado"})

    @api.depends("archivo_firmado_por_usuario")
    def _compute_firmas(self):
        for acta in self:
            archivo = acta.archivo_firmado_por_usuario

            if not archivo:
                acta.write({'firmas_ids': [(5, 0, 0)]})
                continue

            try:
                firmas_json = subprocess.run(
                    [
                        'java',
                        '-XX:CompressedClassSpaceSize=64m',  # Fix for "Could not allocate metaspace", 1GB by default
                        '-Xmx512m',  # Fix for "(malloc) failed to allocate  bytes for Chunk::new", 8GB by default
                        '-jar',
                        '/opt/firma-digital.jar',
                        'verify',
                    ],
                    input=archivo,
                    capture_output=True, check=True
                ).stdout
            except subprocess.CalledProcessError as e:
                print(e.cmd)
                print(e.returncode)
                print(e.output)
                print(e.stderr)
                raise

            try:
                firmas = json.loads(firmas_json)
            except ValueError:
                print('Error parseando firmas JSON')
                print(firmas_json)
                raise

            acta.write({'firmas_ids': [(5, 0, 0)]})

            for firma in firmas[0]['certificado']:
                fecha_hora = dateutil.parser.isoparse(firma['generated'])
                # fecha_hora = fecha_hora.astimezone(dateutil.tz.gettz('America/Guayaquil'))  # Convertir a hora local
                fecha_hora = fecha_hora.replace(tzinfo=None)  # Make it naive, Datetime field only supports naive

                acta.write({'firmas_ids': [(0, 0, {
                    'cedula': firma['datosUsuario']['cedula'],
                    'apellidos': firma['datosUsuario']['apellido'],
                    'nombres': firma['datosUsuario']['nombre'],
                    'entidad': firma['datosUsuario']['entidadCertificadora'],
                    'fecha_hora': fecha_hora,
                    'es_valida': firma['datosUsuario']['certificadoDigitalValido'],
                })]})

            # Validación firmas
            firmas_presentes = set(acta.firmas_ids.mapped('cedula'))

            for field in ('elabora_id', 'aprueba_id', 'user_id'):
                user = getattr(acta, field)
                if user.vat not in firmas_presentes:
                    acta.es_firma_valida = False
                    raise ValidationError(f'La firma de {user.partner_id.name} - {user.partner_id.vat} no está presente en el archivo')

            acta.es_firma_valida = True


    @api.depends('archivo_firmado')
    def _compute_certificate(self):
        for acta in self:
            # acta.certificate_ids = []

            if not acta.archivo_firmado:
                acta.write({'certificate_ids': [(5, 0, 0)]})
                continue

            pdfdata = base64.decodebytes(acta.archivo_firmado)

            n = pdfdata.find(b'/ByteRange')
            start = pdfdata.find(b'[', n)
            stop = pdfdata.find(b']', start)

            if n == -1 or start == -1 or stop == -1:
                # acta.certificate_ids = []
                return

            br = [int(i, 10) for i in pdfdata[start + 1:stop].split()]
            contents = pdfdata[br[0] + br[1] + 1:br[2] - 1]
            data = []
            for i in range(0, len(contents), 2):
                data.append(int(contents[i:i + 2], 16))
            bcontents = bytes(data)
            data1 = pdfdata[br[0]: br[0] + br[1]]
            data2 = pdfdata[br[2]: br[2] + br[3]]
            # signedData = data1 + data2

            datas = bcontents

            signed_data = cms.ContentInfo.load(datas)['content']

            for cert in signed_data['certificates']:
                acta.write({'certificate_ids': [(0, 0, {
                    'certificate_issuer': cert.native['tbs_certificate']['issuer']['common_name'],
                    'certificate_subject': cert.native['tbs_certificate']['subject']['common_name'],
                })]})

            # company.certificate_not_valid_before = certificate.not_valid_before
            # company.certificate_not_valid_after = certificate.not_valid_after
            # company.certificate_issuer = certificate.issuer.rfc4514_string()
            # company.certificate_subject = certificate.subject.rfc4514_string()


class ActaConfidencialidadFirma(models.Model):
    _name = 'acta.confidencialidad.firma'

    acta_confidencialidad_id = fields.Many2one('acta.confidencialidad', required=True, ondelete='cascade')

    cedula = fields.Char(strig='Cédula')
    apellidos = fields.Char(strig='Cédula')
    nombres = fields.Char(strig='Cédula')
    entidad = fields.Char(strig='Cédula')
    fecha_hora = fields.Datetime(strig='Fecha')
    es_valida = fields.Boolean(string='Es válida')


class ActaConfidencialidadOficio(models.Model):
    _name = 'acta.confidencialidad.oficio'

    acta_confidencialidad_id = fields.Many2one('acta.confidencialidad', required=True, ondelete='cascade')
    name = fields.Char()
