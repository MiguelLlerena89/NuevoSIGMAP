import base64
import uuid
import qrcode
from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import date, datetime

import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class UUID(fields.Field):
    """ Encapsulates an :class:`UUID`. """
    type = 'uuid.UUID'
    column_type = ('uuid', 'uuid')

    def convert_to_column(self, value, record, values=None, validate=True):
        return str(value)

    def convert_to_cache(self, value, record, validate=True):
        return str(value)

    def convert_to_record(self, value, record):
        if not value:
            return None
        return uuid.UUID(value)

    def convert_to_read(self, value, record, use_name_get=True):
        return str(value)

    def convert_to_export(self, value, record):
        if value:
            return str(value)
        return ''


class DocumentoEmitido(models.Model):
    _name = "tramite.documento.emitido"
    _description = "Documentos emitidos"
    _inherit = ["mail.thread", "mail.activity.mixin", "tramite.documento.firma"]
    #Agregar enlace de documento realizado

    def _default_company(self):
        return self.env.user.company_id

    uuid = UUID(default=lambda self: uuid.uuid4(), index=True)
    name = fields.Char(translate=True)
    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True
    )

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    resource_ref = fields.Reference(string='Record', selection='_selection_target_model')
    tramite_id = fields.Many2one("tramite", string=_("Trámite"), tracking=True)
    reparto_id = fields.Many2one(related='tramite_id.reparto_id', store=True)
    servicio_id = fields.Many2one(related='tramite_id.servicio_id', string=_("Documento"), tracking=True)
    model_model = fields.Char(related="tramite_id.servicio_id.model_model")
    model_name = fields.Char(related="tramite_id.servicio_id.model_name")
    action_report_id = fields.Many2one(related="tramite_id.servicio_id.action_report_id")
    personal_maritimo_id = fields.Many2one(related="tramite_id.personal_maritimo_id", string=_("Persona"), tracking=True, store=True)
    url_to_action = fields.Char("Enlace al registro")
    tipo_documento_id = fields.Many2one(related='tramite_id.tipo_documento_id', string=_("Tipo Documento"), store=True, tracking=True, readonly=True)
    expediente_archivo = fields.Boolean(string=_("Expediente en archivo?"), default=False, tracking=True)

    fecha_inicio = fields.Date(
        string='Fecha inicio',
        index=True,
        copy=False,
        tracking=True,
        default=fields.Date.today
    )
    fecha_caducidad = fields.Date(
        string='Fecha caducidad',
        index=True,
        copy=False,
        tracking=True,
        compute='_calcular_periodo_caducidad',
    )

    state = fields.Selection([
        ('en_tramite', 'En Trámite'),
        ('por_supervisar', 'Por supervisar'),
        ('por_firmar', 'Por Aprobar'),
        ('vigente', 'Vigente'),
        ('descartado', 'Descartado'),
        ('utilizado', 'Utilizado'),
        ('suspendido', 'Suspendido'),
        ('por_caducar', 'Por caducar'),
        ('caducado', 'Caducado'),
        ('anulado', 'Anulado'),
    ], string='Estado Documento Emitido', default='en_tramite', index=True, copy=False, tracking=True)

    qr_code = fields.Binary("QR Code", compute='_compute_qr_code')
    data = fields.Binary(_('File'), attachment=True)
    filename = fields.Char(_('File Name'))

    fecha_emision = fields.Datetime('Fecha Emisión', readonly=True, index=True, copy=False, tracking=True)

    caducado = fields.Boolean(string='¿Caducado?', compute='_compute_caducado', store=True) #, default=False
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)

    @api.depends('fecha_caducidad')
    def _compute_caducado(self):
        for doc in self:
            today = fields.Date.context_today(self)
            doc.caducado = bool(doc.fecha_caducidad and doc.fecha_caducidad < today)

    _sql_constraints = [
        ('tramite_id_uniq', 'unique (tramite_id)', 'Tramite must be unique.')
    ]

    def _check_tramite_documento_emitido(self, vals):
        tramite_id = self.env['tramite'].browse(vals['tramite_id'])
        if not tramite_id.servicio_id.model_id:
            raise ValidationError(_('Debe configurar el modelo para el servicio: %s.') % (tramite_id.servicio_id.name))
        return tramite_id

    @api.model
    def create(self, vals):
        tramite_id = self._check_tramite_documento_emitido(vals)
        if 'name' not in vals:
            vals["name"] = self.env["ir.sequence"].next_by_code("documento_emitido_sequence_code")
        res = super().create(vals)
        model_model = res.tramite_id.servicio_id.model_model
        data = {
            "documento_emitido_id": res.id
        }
        documento = self.env[model_model].create(data)
        if documento:
            res.resource_ref = f'{model_model},{documento.id}'
            tramite_id.resource_ref = f'{model_model},{documento.id}'
        return res

    def action_send_email(self):
        self.ensure_one()
        mail_template = self.env.ref('tramite.email_template_tramite_documento_emitido')
        if self.state in ['vigente']:
            name = self.archivo_firmado_filename
            attachment = self.env['ir.attachment'].create({
                'name': name,
                'type': 'binary',
                'datas': self.archivo_firmado,
                'store_fname': name,
                'res_model': self._name,
                'res_id': self.id,
                'mimetype': 'application/x-pdf'
            })
            mail_template.attachment_ids = [(6,0, [attachment.id] )]
            mail_template.send_mail(self.id, force_send=True)
            mail_template.attachment_ids = [(3, attachment.id )]
        else:
            mail_template.send_mail(self.id, force_send=True)

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            self.action_send_email()

    @api.depends('fecha_inicio', 'tramite_id')
    def _calcular_periodo_caducidad(self):
        for rec in self:
            if rec.fecha_inicio and rec.tramite_id.servicio_id.caducidad:
                periodo_caducidad = str(rec.tramite_id.servicio_id.periodo_caducidad)
                caducidad = int(rec.tramite_id.servicio_id.caducidad)
                rec.fecha_caducidad = rec.fecha_inicio + relativedelta(**{periodo_caducidad:+ int(caducidad)}) #(periodo_caducidad=+caducidad)
            else:
                rec.fecha_caducidad = None

    def name_get(self):
        result = []
        for rec in self:
            name_info = ''
            name = rec.name
            model_model = rec.model_name
            if rec.personal_maritimo_id:
                name_info = rec.personal_maritimo_id.name
            elif rec.nave_id:
                name_info = rec.nave_id.name
            name = '%s %s %s' % (model_model, name_info, name)
            result.append((rec.id, name))
        return result

    @api.model
    def validar_como_requerido(self, **kwargs):
        # Busca documento emitido vigente al mismo sujeto (nave/persona de mar)
        model = kwargs['model']
        tipo_documento_id = kwargs['tipo_documento_id']

        dom = [
            ('state', '=', 'vigente'),
        ]

        if tipo_documento_id.id == self.env.ref('base_sigmap.gente_mar').id:
            personal_maritimo_id = kwargs['personal_maritimo_id']
            dom.append(('personal_maritimo_id', '=', personal_maritimo_id))
        elif tipo_documento_id.id == self.env.ref('base_sigmap.nave').id:
            nave_id = kwargs['nave_id']
            dom.append(('nave_id', '=', nave_id.id))

        record = self.env[model].search(dom, limit=1, order='create_date desc')
        return record, bool(record)

    def _prepare_report_data(self):
        model_documento = self.model_model
        if not self.action_report_id:
            raise ValidationError('El servicio %s no tiene configurado la plantilla del reporte.' % (model_documento))
        return self.action_report_id

    def _prepare_file_name(self):
        report_titulo_name = self.servicio_id.name
        if self.tipo_documento_id.id == self.env.ref("base_sigmap.gente_mar").id:
            report_titulo_name = '%s - %s' % (report_titulo_name, self.personal_maritimo_id.name)
        return report_titulo_name

    def get_model(self):
        return self.model_model

    def get_model_model_record(self):
        doc = self.env[self.model_model].search([("documento_emitido_id", "=", self.id),], limit=1)
        return doc

    def validar(self):
        pass

    def action_generar_documento(self):
        self.validar()
        action_report_id = self._prepare_report_data()
        report = self.env.ref(action_report_id.report_name)
        doc = self.get_model_model_record()
        action_report = report
        doc.sudo().write({'state': 'por_supervisar', 'fecha_emision': fields.Datetime.now()})
        return action_report

    def _get_sumilla_documento(self):
        res = []
        ref_sumilla = []
        result = ''

        if self.elabora_id:
            ref_sumilla.append(self.elabora_id.sumilla_autor)
            result = '/'.join((ref_sumilla))
        if self.supervisa_id:
            ref_sumilla.append(self.supervisa_id.sumilla)
            result = '/'.join((ref_sumilla))
        res.append({'sumilla': result if len(result) > 0 else 'NO DISPONIBLE'})
        print(res)
        return res

    def _compute_qr_code(self):
        for rec in self:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=4,
            )
            qr.add_data("UUID: ")
            qr.add_data(rec.uuid)
            qr.add_data("\nReparto : ")
            qr.add_data(rec.reparto_id.siglas if rec.reparto_id else "")
            qr.add_data("\nDocumento : ")
            qr.add_data(rec.servicio_id.name)
            qr.add_data("\nEmitido : ")
            qr.add_data(rec.fecha_emision or "NA")
            qr.add_data("\nCaduca : ")
            qr.add_data(rec.fecha_caducidad or "NA")
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            rec.update({'qr_code': qr_image})

    def action_previsualizar(self):
        self.ensure_one()
        self.validar()
        action_report_id = self._prepare_report_data()
        action_report_id.report_type = 'qweb-html'
        doc = self.get_model_model_record()
        result = action_report_id.report_action(doc.id)
        return result

class Tramite(models.Model):
    _inherit = "tramite"

    def action_iniciar_tramite(self):
        super().action_iniciar_tramite()
        modelo = self.servicio_id.model_model
        documento_emitido_id = self.env['tramite.documento.emitido'].create({
            "tramite_id": self.id
            })
        doc = documento_emitido_id.resource_ref

        body = _('Se ha generado %s, %s', self.servicio_id.name, doc._get_html_link())
        self.message_post(body=body)

    def action_entregar(self):
        modelo = self.servicio_id.model_model
        doc = self.env['tramite.documento.emitido'].search([
            ("tramite_id", "=", self.id ),
        ], limit=1)
        if doc:
            self.state = "sent"
        else:
            raise ValidationError(_('Los documentos a entregar, no han sido emitidos'))


class TramiteRequisito(models.Model):
    _inherit = "tramite.requisito"

    completado = fields.Boolean(string=_("Completado?"),
        default=False, store=True, tracking=True,
        compute='_compute_completado',
        inverse='_inverse_completado_edit'
        )

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    documento_emitido_id = fields.Many2one(
        "tramite.documento.emitido",
        string=_("Documento emitido"),
        compute='_compute_completado',
        inverse='_inverse_completado_edit',
        tracking=True
        )

    documento_ref = fields.Reference(string='Documento', selection='_selection_target_model')

    fecha_caducidad = fields.Date(
        string="Fecha caducidad",
        tracking=True,
    )

    @api.depends('requisito_id', 'tramite_id.curso_id', 'tramite_id.jerarquia_id')
    def _compute_completado(self):
        for requisito in self:
            modelo_tramite = requisito.tramite_id.servicio_id.model_model
            if not modelo_tramite:
                requisito.completado = False
                break
            modelo_requisito = requisito.requisito_id.documento_requerido_id.model_model

            personal_maritimo_id = requisito.tramite_id.personal_maritimo_id
            if modelo_requisito:
                curso_id = requisito.tramite_id.curso_id
                jerarquia_id = requisito.tramite_id.jerarquia_id
                nave_id = requisito.tramite_id.nave_id
                servicio_id = requisito.requisito_id.documento_requerido_id
                doc, es_completado = self.env[modelo_requisito].validar_como_requerido(
                    model=modelo_requisito,
                    tipo_documento_id=self.tramite_id.tipo_documento_id,
                    personal_maritimo_id=personal_maritimo_id,
                    curso_id=curso_id,
                    jerarquia_id=jerarquia_id,
                    nave_id=nave_id,
                    servicio_id=servicio_id,
                )
                if doc:
                    if hasattr(doc, '_name') and hasattr(doc, 'id'):
                        requisito.documento_ref = f'{doc._name},{doc.id}'
                    requisito.fecha_caducidad = doc.fecha_caducidad
                    requisito.completado = es_completado
                    requisito.name = doc.name
                else:
                    requisito.completado = False
                    requisito.name = False
                    requisito.fecha_caducidad = False

    def _inverse_completado_edit(self):
        pass
