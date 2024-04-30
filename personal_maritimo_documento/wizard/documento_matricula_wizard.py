from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class DocumentoMatriculaWizard(models.TransientModel):
    _name = 'documento.matricula.wizard'
    _description = 'Documento Matricula Wizard'

    motivo_id = fields.Many2one("matricula.motivo", string="Control impresión", tracking=True)
    # motivo = fields.Selection(
    #     selection=lambda self: self.env['matricula.control'].fields_get(['motivo'])['motivo']['selection'],
    #     string='Control impresión', index=True, copy=False, tracking=True)
    motivo_reimpresion = fields.Text('Descripción del Motivo de Reimpresión')

    @api.constrains('motivo_reimpresion')
    def check_motivo_reimpresion(self):
        if len(self.motivo_reimpresion) == 0:
            raise ValidationError('Debe adicionar el motivo de la reimpresión.')

    carnet_id = fields.Many2one('permar.documento.carnet', string='Carnet')
    libretin_id = fields.Many2one('permar.documento.libretin', string='Libretin')

    def action_registro_motivo(self):
        self.ensure_one()
        report_id = ''
        docid = ''
        if self.carnet_id:
            if not self.carnet_id.es_provisional:
                report_id = 'personal_maritimo_documento.action_report_documento_carnet'
                docid = self.carnet_id.id
                self.carnet_id.write({
                    "state": "vigente",
                    "control_ids": [(0, 0, {
                        "name": "Reimpresión carnet",
                        "motivo_id": self.motivo_id.id,
                        # "motivo": self.motivo,
                        "motivo_reimpresion": self.motivo_reimpresion,
                        }
                    )]
                })
                msg = "Se ha reimpreso la Matrícula de Tráfico Nacional para %s " % (self.carnet_id.personal_maritimo_id.name)
                self.carnet_id.message_post(body=msg)
            else:
                ctx = dict(
                    default_carnet_id = self.carnet_id.id,
                    es_provisional = bool(self.carnet_id.es_provisional),
                    reimprimir = True,
                    motivo_id = self.motivo_id.id,
                    motivo_reimpresion = self.motivo_reimpresion,
                )
                return self.carnet_id.action_nuevo_formato_wizard(ctx)

        if self.libretin_id:
            ctx = dict(
                default_libretin_id = self.libretin_id.id,
                es_provisional = bool(self.libretin_id.es_provisional),
                reimprimir = True,
                motivo_id = self.motivo_id.id,
                motivo_reimpresion = self.motivo_reimpresion,
            )
            return self.libretin_id.action_nuevo_formato_wizard(ctx)
            # report_id = 'personal_maritimo_documento.action_report_documento_libretin'
            # docid = self.libretin_id.id
            # self.libretin_id.write({
            #     "state": "vigente",
            #     "control_ids": [(0, 0, {
            #         "name": "Reimpresión libretin",
            #         "motivo_id": self.motivo_id.id,
            #         # "motivo": self.motivo,
            #         "motivo_reimpresion": self.motivo_reimpresion,
            #         }
            #     )]
            # })
            # msg = "Se ha reimpreso la Matrícula de Tráfico Internacional para %s " % (self.libretin_id.personal_maritimo_id.name)
            # self.libretin_id.message_post(body=msg)

        report_action = self.env.ref(report_id).report_action(docid)
        report_action.update({'close_on_report_download': True})
        return report_action
