from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import content_disposition, request

class Dotacion(models.Model):
    _inherit = 'permar.documento.dotacion'

    def button_imprimir(self):
        ctx = dict(
            default_dotacion_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)


class RefrendoTituloFormacion(models.Model):
    _inherit = 'permar.documento.refrendo.titulo.formacion'

    def button_imprimir(self):
        ctx = dict(
            default_refrendo_titulo_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)


class CertificadoCompetencia(models.Model):
    _inherit = 'permar.documento.certificado.competencia'

    def button_imprimir(self):
        ctx = dict(
            default_certificado_competencia_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)


class CertificadoSuficiencia(models.Model):
    _inherit = 'permar.documento.certificado.suficiencia'

    def action_print_certificado_suficiencia(self):
        ctx = dict(
            default_certificado_suficiencia_id = self.id,
            default_certificado_suficiencia = 'certificado_suficiencia',
        )
        return self.action_nuevo_formato_wizard(ctx)

    def action_print_libretin_certificado_suficiencia(self):
        ctx = dict(
            default_certificado_suficiencia_id = self.id,
            default_libretin_certificado_suficiencia = 'libretin_certificado_suficiencia',
        )
        return self.action_nuevo_formato_wizard(ctx)


class CertificadoMedico(models.Model):
    _inherit = 'permar.documento.refrendo.certificado.medico'

    def action_print_certificado_medico(self):
        ctx = dict(
            default_refrendo_medico_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)


class ReconocimientoTitulo(models.Model):
    _inherit = 'permar.documento.reconocimiento.titulo'

    def button_imprimir(self):
        ctx = dict(
            default_reconocimiento_titulo_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)


class PermisoProvisionalEmbarque(models.Model):
    _inherit = 'permar.documento.permiso.provisional.embarque'

    def button_imprimir(self):
        ctx = dict(
            default_permiso_provisional_embarque_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)


class EvaluacionCompetencia(models.Model):
    _inherit = 'permar.documento.convalidacion.competencia'

    def button_imprimir(self):
        ctx = dict(
            default_evaluacion_competencia_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)


class ConvalidacionCompetencia(models.Model):
    _inherit = 'permar.documento.convalidacion.competencia'

    def button_imprimir(self):
        ctx = dict(
            default_convalidacion_competencia_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)

class Dispensa(models.Model):
    _inherit = 'permar.documento.dispensa'

    def button_imprimir(self):
        ctx = dict(
            default_dispensa_id = self.id,
        )
        return self.action_nuevo_formato_wizard(ctx)

class DocumentoCarnet(models.Model):
    _inherit = 'permar.documento.carnet'

    def button_imprimir_provisional(self):
        super().button_imprimir_provisional()
        ctx = dict(
            default_carnet_id = self.id,
            es_provisional = bool(self.es_provisional),
        )
        return self.action_nuevo_formato_wizard(ctx)

class DocumentoLibretin(models.Model):
    _inherit = 'permar.documento.libretin'

    def button_imprimir(self):
        super().button_imprimir()
        ctx = dict(
            default_libretin_id = self.id,
            es_provisional = bool(self.es_provisional),
        )
        return self.action_nuevo_formato_wizard(ctx)

    # def button_reimprimir(self):
    #     super().button_reimprimir()
    #     ctx = dict(
    #         default_libretin_id = self.id,
    #         es_provisional = bool(self.es_provisional),
    #         reimprimir = True,
    #         motivo_id = self.motivo_id.id,
    #         motivo_reimpresion = self.motivo_reimpresion,
    #     )
    #     return self.action_nuevo_formato_wizard(ctx)

    def button_imprimir_provisional(self):
        super().button_imprimir_provisional()
        ctx = dict(
            default_libretin_id = self.id,
            es_provisional = bool(self.es_provisional),
        )
        return self.action_nuevo_formato_wizard(ctx)


class DocumentoNumeroFormato(models.TransientModel):
    _name = 'documento.numero.formato'
    _description = 'Número de Formato de Impresión'

    numero_formato = fields.Integer(string="Número de Formato de Seguridad")

    @api.constrains('numero_formato')
    def check_numero_formato(self):
        if not self.numero_formato or self.numero_formato <= 0:
            raise ValidationError('Número de formato inválido.')


    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([
            ("model", "in", [])
        ])]

    resource_ref = fields.Reference(string='Record', selection='_selection_target_model')

    refrendo_titulo_id = fields.Many2one('permar.documento.refrendo.titulo.formacion', string="Refrendo Título")
    certificado_competencia_id = fields.Many2one('permar.documento.certificado.competencia', string="Certificado de Competencia")
    refrendo_medico_id = fields.Many2one('permar.documento.refrendo.certificado.medico', string="Refrendo de Certificado Médico")
    certificado_suficiencia_id = fields.Many2one('permar.documento.certificado.suficiencia', string="Certificado Suficiencia")
    reconocimiento_titulo_id = fields.Many2one('permar.documento.reconocimiento.titulo', string="Reconocimiento Título")
    permiso_provisional_embarque_id = fields.Many2one('permar.documento.permiso.provisional.embarque', string="Permiso Provisional de Embarque")
    evaluacion_competencia_id = fields.Many2one('permar.documento.convalidacion.competencia', string="Evaluación de Competencia")
    convalidacion_competencia_id = fields.Many2one('permar.documento.convalidacion.competencia', string="Convalidación de Competencia")
    dispensa_id = fields.Many2one('permar.documento.dispensa', string="Dispensa")
    dotacion_id = fields.Many2one('permar.documento.dotacion', string="Dotación")

    carnet_id = fields.Many2one('permar.documento.carnet', string="Carnet")
    libretin_id = fields.Many2one('permar.documento.libretin', string="Libretin")

    def _prepare_report_data(self):
        action_report_id = ''
        docid = ''

        # Revisar reporte a partir de modelo

        if self.refrendo_titulo_id:
            action_report_id = 'personal_maritimo_documento.action_report_refrendo_titulo'
            docid = self.refrendo_titulo_id.id

        if self.certificado_competencia_id:
            action_report_id = 'personal_maritimo_documento.action_report_titulocompetencia'
            docid = self.certificado_competencia_id.id

        if self.certificado_suficiencia_id:
            context = self.env.context
            self.ensure_one()
            if context.get('default_certificado_suficiencia'):
                action_report_id = 'personal_maritimo_documento.action_report_titulosuficiencia'
            else:
                action_report_id = 'personal_maritimo_documento.action_report_libretin_certificado_suficiencia'
            docid = self.certificado_suficiencia_id.id

        if self.refrendo_medico_id:
            action_report_id = 'personal_maritimo_documento.action_report_certificado_medico'
            docid = self.refrendo_medico_id.id

        if self.reconocimiento_titulo_id:
            action_report_id = 'personal_maritimo_documento.action_report_reconocimiento_titulo'
            docid = self.reconocimiento_titulo_id.id

        if self.permiso_provisional_embarque_id:
            action_report_id = 'personal_maritimo_documento.action_report_permiso_provisional_embarque'
            docid = self.permiso_provisional_embarque_id.id

        if self.evaluacion_competencia_id:
            action_report_id = 'personal_maritimo_documento.action_report_evaluacion'
            docid = self.evaluacion_competencia_id.id

        if self.convalidacion_competencia_id:
            action_report_id = 'personal_maritimo_documento.action_report_convalidacion'
            docid = self.convalidacion_competencia_id.id

        if self.dispensa_id:
            action_report_id = 'personal_maritimo_documento.action_report_dispensa'
            docid = self.dispensa_id.id

        if self.dotacion_id:
            action_report_id = 'personal_maritimo_documento.action_report_dotacion'
            docid = self.dotacion_id.id

        if self.carnet_id:
            action_report_id = 'personal_maritimo_documento.action_report_documento_carnet_provisional'
            docid = self.carnet_id.id

        if self.libretin_id:
            es_provisional = self.env.context.get('es_provisional')
            if not es_provisional:
                action_report_id = 'personal_maritimo_documento.action_report_documento_libretin'
            else:
                action_report_id = 'personal_maritimo_documento.action_report_documento_libretin_provisional'
            docid = self.libretin_id.id

        return action_report_id, docid

    def action_imprimir_documento(self):
        self.ensure_one()
        action_report_id, docid = self._prepare_report_data()

        report = self.env.ref(action_report_id)
        active_model = report.model
        modelo_titulo_id = self.env[active_model].browse(docid)
        if not modelo_titulo_id.documento_emitido_id.tramite_id.servicio_id.titulo_reporte or not modelo_titulo_id.documento_emitido_id.tramite_id.servicio_id.titulo_reporte_en:
            raise UserError("Debe configurar la descripción en español e inglés del título de encabezado de reporte del servicio: %s." % (modelo_titulo_id.documento_emitido_id.tramite_id.servicio_id.name))
        #modelo_titulo_id.sudo().write({'numero_formato': self.numero_formato})

        msg = ''
        descripcion = ''
        if active_model in ['permar.documento.carnet', 'permar.documento.libretin']:
            data_control_impresion = {"name": ""}
            if self.env.context.get('reimprimir'):
                data_control_impresion["motivo_id"] = int(self.env.context.get('motivo_id'))
                data_control_impresion["motivo_reimpresion"] = self.env.context.get('motivo_reimpresion')
                descripcion = "Reimpresión de "
            else:
                descripcion = "Impresión de "
            descripcion = descripcion + active_model.split('.')[-1]
            if self.env.context.get('es_provisional'):
                descripcion = descripcion + " provisional"

            data_control_impresion["name"] = descripcion
            modelo_titulo_id.sudo().write({
                "state": "vigente",
                "numero_formato": self.numero_formato,
                "control_ids": [(0, 0, data_control_impresion)]
            })
            msg = "Se ha reimpreso el %s con número de formato de seguridad: %s "
        else:
            msg = "Se ha impreso el %s con número de formato de seguridad: %s "
            modelo_titulo_id.sudo().write({'numero_formato': self.numero_formato})

        msg = msg % (modelo_titulo_id.documento_emitido_id.name_get()[0][1], str(self.numero_formato))
        modelo_titulo_id.message_post(body=msg)

        data = {
            'active_model': active_model,
            'active_ids': docid,
            'docs': modelo_titulo_id,
        }
        #report_action = report.report_action(docid, data=data)
        report_action = report.report_action(docid)
        #report_action = self.env.ref(report_id).report_action(docid)
        report_action.update({'close_on_report_download': True})
        return report_action