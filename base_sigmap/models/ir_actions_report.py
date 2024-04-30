import re
import base64
import io

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from odoo.tools import pdf
from odoo.tools import html2plaintext

from odoo import fields, models, tools, api, _
from odoo.exceptions import ValidationError, AccessError, UserError

from ast import literal_eval
from pathlib import Path


IMAGE_FILE = Path('../static/src/img/a4dirnea.jpg')

import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    imagen_fondo_documento = fields.Binary(string='Imagen de Fondo de Documentos', attachment=True)
    report_no_background_ids = fields.Many2many('ir.actions.report', string=_('Reportes excluyentes para imagen de fondo en documentos'))

    def _check_jpeg_format(self, data):
        if data[:2] != b'\xFF\xD8':
            return False
        return True

    @api.constrains("imagen_fondo_documento")
    def _check_imagen_fondo_documento(self):
        for rec in self:
            if rec.imagen_fondo_documento:
                decoded_image = base64.b64decode(rec.imagen_fondo_documento)
                if not self._check_jpeg_format(decoded_image):
                    raise ValidationError(_('Formato de imagen JPEG no válido'))

    def set_values(self):
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('base_sigmap.imagen_fondo_documento', self.imagen_fondo_documento)
        params.set_param('base_sigmap.report_no_background_ids', self.report_no_background_ids.ids)


    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        report_ids = params.get_param('base_sigmap.report_no_background_ids')
        lista_report = [(6, 0, literal_eval(report_ids))] if report_ids else False
        res.update(
            imagen_fondo_documento=params.get_param('base_sigmap.imagen_fondo_documento'),
            report_no_background_ids=lista_report
        )
        return res


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        result = super(IrActionsReport, self)._render_qweb_pdf_prepare_streams(
            report_ref, data, res_ids=res_ids
        )
        if not res_ids:
            return result
        report = self._get_report(report_ref)
        imagen_fondo_documento = self.env['ir.config_parameter'].sudo().get_param('base_sigmap.imagen_fondo_documento')
        report_no_background_ids = self.env['ir.config_parameter'].sudo().get_param('base_sigmap.report_no_background_ids')
        if report_no_background_ids:
            report_ids = literal_eval(report_no_background_ids)
            if report.id not in report_ids:
                # Leer la imagen de fondo desde un archivo
                # if imagen_fondo_documento:
                #     with open(imagen_fondo_documento, 'wb') as f:
                #         background_image_data = base64.b64encode(f.read())
                # else:
                #     image_path = Path(__file__).absolute().parent / IMAGE_FILE
                #     with open(image_path, 'rb') as f:
                #         background_image_data = f.read()

                image_path = Path(__file__).absolute().parent / IMAGE_FILE
                with open(image_path, 'rb') as f:
                    background_image_data = f.read()

                with io.BytesIO(base64.b64decode(background_image_data)) as stream:
                    for res_id in result:
                        pdf_writer = pdf.PdfFileWriter()
                        pdf_reader = pdf.PdfFileReader(result[res_id]["stream"])

                        packet = io.BytesIO()
                        canvas = Canvas(packet, pagesize=A4)
                        canvas.setFillColorRGB(255, 255, 255)

                        image = ImageReader(io.BytesIO(background_image_data))
                        canvas.drawImage(image, 0, 0, width=A4[0], height=A4[1])

                        canvas.showPage()
                        canvas.save()
                        packet.seek(0)

                        for page_no in range(0, pdf_reader.numPages):
                            new_page = PdfFileReader(packet).getPage(0)
                            new_page.mergePage(pdf_reader.getPage(page_no))
                            pdf_writer.addPage(new_page)

                        new_stream = io.BytesIO()
                        pdf_writer.write(new_stream)
                        result[res_id]["stream"] = new_stream
        return result