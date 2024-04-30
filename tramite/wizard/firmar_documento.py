from odoo import _, api, fields, models


class DocumentoFirmarWizard(models.TransientModel):
    _name = 'tramite.documento.firmar.wizard'

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    documento_ref = fields.Reference(string='Documento', selection='_selection_target_model')
    password = fields.Char(_('Contraseña'))
    action = fields.Selection([
        ('supervisar', 'Supervisar'),
        ('aprobar', 'Aprobar'),
    ])

    def action_confirmar(self):
        self.ensure_one()
        self.documento_ref.firmar_archivo(self.password, self.action)
