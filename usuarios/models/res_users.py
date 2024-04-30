# -*- coding: utf-8 -*-
import base64
import logging
from cryptography.hazmat.primitives.serialization import pkcs12

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, AccessDenied
from odoo.http import request



_logger = logging.getLogger(__name__)


class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    state = fields.Selection(selection_add=[
        ('incomplete', _('Incompleto')),
        ('to_aprove', _('Por aprobar')),
        ('new',)
    ])

    acta_confidencialidad_ids = fields.One2many('acta.confidencialidad', 'user_id', string='Actas de confidencialidad')

    oficio_ids = fields.One2many('sigmap.oficio.usuario', 'user_id', string='Oficios')

    es_externo = fields.Boolean('Externo', default=False)

    reparto_id = fields.Many2one('sigmap.reparto',
                                 default=lambda self: self.env.user.reparto_id,
                                 domain=lambda self: [('id', 'child_of', self.env.user.reparto_id.id)]
                                                    if self.env.ref('base.group_system').id not in self.env.user.groups_id.ids
                                                    else [])
    departamento_id = fields.Many2one('sigmap.departamento')
    cargo_id = fields.Many2one('sigmap.cargo')
    rango_id = fields.Many2one('tipo.rango', string='Grado')
    rango_abreviatura = fields.Char(related='rango_id.abreviatura', string='Grado abreviatura')
    especialidad_id = fields.Many2one('sigmap.especialidad')
    especialidad_abreviatura = fields.Char(related='especialidad_id.abreviatura', string='Especialidad abreviatura')
    profesion_abreviatura = fields.Char('Profesión abreviatura', compute='_compute_profesion_abreviatura')

    entidad_externa_id = fields.Many2one('sigmap.entidad.externa')
    distribuidora_id = fields.Many2one('sigmap.distribuidora')

    sumilla = fields.Char('Sumilla', copy=False, tracking=True)
    sumilla_autor = fields.Char('Sumilla como autor', copy=False, tracking=True, help="Concatenado del primer carácter del nombre y primer apellido completo del usuario.")

    certificate = fields.Binary('Certificado electrónico', tracking=True, copy=False)
    certificate_filename = fields.Char(string="Nombre de archivo de certificado electrónico", tracking=True, copy=False)
    certificate_password = fields.Char('Contraseña certificado', size=255)
    certificate_not_valid_before = fields.Date(string="Válido desde", compute='_compute_certificate', store=True)
    certificate_not_valid_after = fields.Date(string="Válido hasta", compute='_compute_certificate', store=True)
    certificate_issuer = fields.Char(string='Emisor certificado', compute='_compute_certificate', store=True)
    certificate_subject = fields.Char(string='Emitido certificado', compute='_compute_certificate', store=True)
    certificate_is_valid = fields.Boolean(string='Certificado válido', compute='_compute_certificate', store=True)

    imagen_firma = fields.Image('Foto firma', tracking=True, copy=False)

    texto_firma = fields.Char(string='Texto Firma')

    tipo_funcionario = fields.Selection(
        [('civil', 'Civil'),('militar', 'Militar')],
        string='Tipo de Funcionario', required=True,
        default=False, copy=False, tracking=True)

    tipo_funcionario_civil = fields.Selection(
        [('servidor_publico', 'Servidor Público'), ('particular', 'Particular')],
        string='Tipo de funcionario civil', required=False,
        default=False, copy=False, tracking=True)
    profesion_id = fields.Many2one('sigmap.profesion')

    # Make sure the user state is active (i.e "new" or "active")
    @classmethod
    def _login(cls, db, login, password, user_agent_env):
        uid = super()._login(db, login, password, user_agent_env)
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'

        try:
            with cls.pool.cursor() as cr:
                env = api.Environment(cr, uid, {})
                if env.user.state not in ('new', 'active'):
                    raise AccessDenied('')
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s from %s. User is not active", db, login, ip)
            raise

        return uid

    @api.depends('rango_id', 'especialidad_id', 'tipo_funcionario', 'profesion_id', 'tipo_funcionario_civil')
    def _compute_profesion_abreviatura(self):
        for user in self:
            if user.tipo_funcionario == 'civil':
                if user.tipo_funcionario_civil == 'servidor_publico':
                    user.profesion_abreviatura = '-'.join(filter(None, [
                        'SERPUB',
                        user.profesion_id.abreviatura if user.profesion_id else None
                    ]))
                else:
                    user.profesion_abreviatura = user.profesion_id.abreviatura
            elif user.tipo_funcionario == 'militar':
                user.profesion_abreviatura = '-'.join(filter(None, [
                    user.rango_id.abreviatura if user.rango_id else None,
                    user.especialidad_id.abreviatura if user.especialidad_id else None,
                ]))
            else:
                user.profesion_abreviatura = ''

    def _compute_state(self):
        for user in self:
            if user.id == self.env.ref('base.user_admin').id:
                super()._compute_state()
            else:
                if not user.acta_confidencialidad_ids:
                    user.state = 'incomplete'
                elif not user.acta_confidencialidad_ids.state == 'usuario_activado':
                    user.state = 'to_aprove'
                else:
                    super()._compute_state()

    @api.depends('certificate', 'certificate_password')
    def _compute_certificate(self):
        for company in self:
            company.certificate_not_valid_before = None
            company.certificate_not_valid_after = None
            company.certificate_issuer = None
            company.certificate_subject = None
            company.certificate_is_valid = False

            if not company.certificate or not company.certificate_password:
                continue

            try:
                _, certificate, _ = pkcs12.load_key_and_certificates(base64.decodebytes(company.certificate),
                                                                     company.certificate_password.encode())
            except ValueError:
                continue

            company.certificate_not_valid_before = certificate.not_valid_before
            company.certificate_not_valid_after = certificate.not_valid_after
            company.certificate_issuer = certificate.issuer.rfc4514_string()
            company.certificate_subject = certificate.subject.rfc4514_string()
            company.certificate_is_valid = True

    def preference_save(self):
        if self.certificate and not self.certificate_is_valid:
            raise ValidationError('Certifcado no es válido')

        super().preference_save()

        # Use raw query to avoid trigger api.depends and recalculate
        self.env.cr.execute(f"UPDATE res_users SET certificate_password = '' WHERE id = {self.id}")

    def action_generar_acta_confidencialidad(self):
        for user in self:
            if user.es_externo and not user.entidad_externa_id:
                raise ValidationError('Usuarios externos deben tener definida la entidad externa.')
            if not user.es_externo:
                if user.tipo_funcionario == 'civil':
                    if not all([user.reparto_id, user.departamento_id, user.cargo_id,
                               user.tipo_funcionario_civil, user.profesion_id]):
                        raise ValidationError('Debe tener definido reparto, departamento, cargo, tipo y profesión.')
                elif user.tipo_funcionario == 'militar':
                    if not all([user.reparto_id, user.departamento_id, user.cargo_id,
                               user.rango_id, user.especialidad_id]):
                        raise ValidationError('Debe tener definido reparto, departamento, cargo, grado y especialidad.')
                else:
                    raise ValidationError('El funcionario de ser de tipo civil o militar')

            if not user.reparto_id.responsable_id:
                raise ValidationError('El reparto no tiene configurado un responsable.')

            if not user.oficio_ids:
                raise ValidationError('Debe especificar al menos un oficio.')

            if not user.partner_id.vat:
                raise ValidationError('Persona no tiene identificación configurada.')

            if not user.partner_id.city_id:
                raise ValidationError('Persona no tiene ciudad configurada.')

            acta_confidencialidad = self.env['acta.confidencialidad'].sudo().create({
                'user_id': user.id,
                'es_externo': user.es_externo,
                'reparto_id': user.reparto_id.id,
                'departamento_id': user.departamento_id.id,
                'cargo_id': user.cargo_id.id,
                'especialidad_id': user.especialidad_id.id,
                'rango_id': user.rango_id.id,
                'entidad_externa_id': user.entidad_externa_id.id,
            })

            for oficio in user.oficio_ids:
                acta_confidencialidad.sudo().write({'oficio_ids': [(0, 0, {
                    'name': oficio.name,
                })]})

        return True


class OficioUsuario(models.Model):
    _name = 'sigmap.oficio.usuario'

    user_id = fields.Many2one('res.users', required=True)
    name = fields.Char()
    reparto_id = fields.Many2one('sigmap.reparto', compute='_compute_reparto')
    archivo = fields.Binary()
    archivo_filename = fields.Char()

    @api.depends('user_id')
    def _compute_reparto(self):
        for oficio in self:
            if oficio.user_id and oficio.user_id.reparto_id:
                oficio.reparto_id = oficio.user_id.reparto_id
            else:
                oficio.reparto_id = False
