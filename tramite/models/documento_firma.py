import subprocess
import os
import base64

import fitz

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class DocumentoFirma(models.AbstractModel):
    _name = 'tramite.documento.firma'

    reparto_id = fields.Many2one("sigmap.reparto", string="Reparto",
                                 default=lambda self: self.env.user.reparto_id,
                                 readonly=True, tracking=True)

    elabora_id = fields.Many2one("res.users", string=_("Elaborado por"), readonly=True, tracking=True,
                                 default=lambda self: self.env.user)
    supervisa_id = fields.Many2one("res.users", string=_("Supervisado por"), readonly=True, tracking=True)
    aprueba_id = fields.Many2one("res.users", string=_("Aprobado por"), readonly=True, tracking=True)

    archivo = fields.Binary(_('Archivo'))
    archivo_filename = fields.Char()
    archivo_firmado = fields.Binary(_('Archivo firmado'), readonly=True)
    archivo_firmado_filename = fields.Char()

    def get_model(self):
        return self._name

    def get_model_model_record(self):
        return self

    def generar_documento(self):
        action_report_id = self._prepare_report_data()
        filename = self._prepare_file_name()

        if not self.elabora_id.sumilla or not self.elabora_id.sumilla_autor:
            raise ValidationError(_('El usuario %s no tiene sumilla registrada.') % (self.elabora_id.name))
        if not self.supervisa_id.sumilla or not self.supervisa_id.sumilla_autor:
            raise ValidationError(_('El usuario %s no tiene sumilla registrada.') % (self.supervisa_id.name))
        if not self.aprueba_id.sumilla or not self.aprueba_id.sumilla_autor:
            raise ValidationError(_('El usuario %s no tiene sumilla registrada.') % (self.aprueba_id.name))
        if self.aprueba_id:
            msg = ''
            if not self.aprueba_id.rango_id:
                msg = msg + '* Rango o grado.\n'
            if not self.aprueba_id.cargo_id:
                msg = msg + '* Cargo.\n'
            # if not self.aprueba_id.especialidad_id:
            #     msg = msg + '* Especialidad.\n'
            # if not self.aprueba_id.texto_firma:
            #     msg = msg + '* Texto para la firma.\n'
            if msg:
                msg ='%s%s' % (('El responsable del reparto %s no tiene configurado: \n' % (self.aprueba_id.name)), msg)
                raise ValidationError(msg)
        doc = self.get_model_model_record()
        report = self.env['ir.actions.report']._render_qweb_pdf(action_report_id, doc.id)
        filename_pdf = filename + '.pdf'
        b64_pdf = base64.b64encode(report[0])
        self.write({
            'archivo': b64_pdf,
            'archivo_filename': filename_pdf,
        })

        attachment = self.env['ir.attachment'].create({
            'name': filename_pdf,
            'type': 'binary',
            'datas': b64_pdf,
            'store_fname': filename_pdf,
            'res_model': self.get_model(),
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })
        return attachment

    def ubicacion_texto(self, archivo, texto):
        pdf = fitz.open(stream=base64.b64decode(self.archivo))
        for page in pdf:
            pos = page.search_for(texto)
            if len(pos) > 0:
                page_height = page.get_text('dict')['height']
                # Push 30px down so QR is vertically centered
                return page.number + 1, int(pos[0].x0), int(page_height - pos[0].y1) - 30

    def ubicacion_sumilla(self):
        return self.ubicacion_texto(self.archivo, 'QRSUPERVISION') or (1, 0, 0)  # First page, lower left

    def ubicacion_firma_responsable(self):
        # Defaults to first page, lower (almost) center
        return self.ubicacion_texto(self.archivo_firmado, 'QRAPROBACION') or (1, 0, 200)

    def firmar_archivo(self, password, action):
        # ensure one?
        for documento in self:
            # Encoded as base64
            if action == 'supervisar':
                documento.write({
                    'supervisa_id': self.env.user,
                    'aprueba_id': self.reparto_id.responsable_id,
                })
                documento.generar_documento()
                archivo = documento.archivo
                archivo_filename = documento.archivo_filename
                page, pos_x, pos_y = self.ubicacion_sumilla()
            elif action == 'aprobar':
                archivo = documento.archivo_firmado
                archivo_filename = documento.archivo_firmado_filename
                page, pos_x, pos_y = self.ubicacion_firma_responsable()
            else:
                raise ValueError(f'Invalid action {action}')
            certificado = self.env.user.certificate

            if not archivo:
                raise ValidationError('No existe archivo para ser firmado')

            if not certificado:
                raise ValidationError('Certificado no ha sido configurado')

            try:
                archivo_firmado = subprocess.run(
                    [
                        'java',
                        '-XX:CompressedClassSpaceSize=64m',  # Fix for "Could not allocate metaspace", 1GB by default
                        '-Xmx512m',  # Fix for "(malloc) failed to allocate  bytes for Chunk::new", 8GB by default
                        '-jar',
                        '/opt/firma-digital.jar',
                        'sign',
                        str(page),
                        str(pos_x),
                        str(pos_y),
                    ],
                    input=archivo + b'\n' + password.encode('utf-8') + b'\n' + certificado,
                    capture_output=True, check=True
                ).stdout
            except subprocess.CalledProcessError as e:
                print(e.cmd)
                print(e.returncode)
                print(e.output)
                print(e.stderr)
                raise

            filename, extension = os.path.splitext(archivo_filename)

            # action -> next_state
            state = {
                'supervisar': 'por_firmar',
                'aprobar': 'vigente',
            }[action]

            documento.write({
                'archivo_firmado': archivo_firmado,
                'archivo_firmado_filename': f'{filename}-signed{extension}',
                'state': state,
            })

    def action_supervisar(self):
        if not self.reparto_id.responsable_id:
            raise ValidationError(f'Reparto {self.reparto_id.siglas} no tiene configurado un responsable')

        return self.action_firmar('supervisar')

    def action_aprobar(self):
        if self.env.user.id != self.aprueba_id.id:
            raise ValidationError('Usted no es el usuario asignado para aprobar este documento')

        return self.action_firmar('aprobar')

    def action_firmar(self, action):
        ctx = {
            'default_documento_ref': f'{self._name},{self.id}',
            'default_action': action,
        }

        action = self.env['ir.actions.actions']._for_xml_id('tramite.action_wizard_firmar_documento_form')
        action.update({
            'context': ctx,
        })

        return action
