from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = ['personal.maritimo']

    reconocimiento_certificado_medico_ids = fields.One2many(
        'permar.documento.reconocimiento.certificado.medico', 'personal_maritimo_id', string='Reconocimientos de títulos',
        help="Reconocimiento certificado médico la persona")
    reconocimiento_certificado_medico_count = fields.Integer(compute='_compute_reconocimiento_certificado_medico_count')

    def _compute_reconocimiento_certificado_medico_count(self):
        for partner in self:
            partner.reconocimiento_certificado_medico_count = len(partner.reconocimiento_certificado_medico_ids)

    def action_open_reconocimiento_certificado_medico(self):
        self.ensure_one()
        return {
            'name': 'Reconocimientos de títulos',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.reconocimiento.certificado.medico',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.reconocimiento_certificado_medico_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class CertificadoMedico(models.Model):
    _inherit = "personal.maritimo.ficha.medica"

    es_reconocimiento = fields.Boolean('Es reconocimiento?', default=False)

class ReconocimientoCertificadoMedico(models.Model):
    _name = "permar.documento.reconocimiento.certificado.medico"
    _description = "Reconocimiento de certificados médicos extranjeros con países de convenio"
    _inherit = "documento.base"

    reparto = fields.Char(string=_("Reparto"), size=100, index=True, tracking=True)
    certificado_medico_id = fields.Many2one('personal.maritimo.ficha.medica')
    country_id = fields.Many2one('res.country')

    es_reconocimiento = fields.Boolean(related='certificado_medico_id.es_reconocimiento', store=True, readonly=False)

    numero_chequeo_vih = fields.Char(related='certificado_medico_id.numero_chequeo_vih', store=True, readonly=False)
    fecha_emision_examen_vih = fields.Date(related='certificado_medico_id.fecha_emision_examen_vih', store=True, readonly=False)
    resultado_vih = fields.Char(related='certificado_medico_id.resultado_vih', store=True, readonly=False)

    proposito_examen = fields.Char(related='certificado_medico_id.numero_ficha_aptitud')
    numero_ficha_aptitud = fields.Char(related='certificado_medico_id.numero_ficha_aptitud', store=True, readonly=False)
    fecha_emision = fields.Date(related='certificado_medico_id.fecha_emision', store=True, readonly=False)
    fecha_caducidad = fields.Date(related='certificado_medico_id.fecha_caducidad', store=True, readonly=False)
    resultado_ficha = fields.Html(related='certificado_medico_id.resultado_ficha', store=True, readonly=False)

    observacion = fields.Html(related='certificado_medico_id.observacion', store=True, readonly=False)
    restriccion = fields.Text(related='certificado_medico_id.restriccion', store=True, readonly=False)

    def write(self, vals):
        super().write(vals)
        res = self
        if not res.certificado_medico_id:
            certificado_medico = self.env['personal.maritimo.ficha.medica'].create({
                "personal_maritimo_id": res.personal_maritimo_id.id,
                "country_id": res.country_id.id,
                "fecha_emision": res.fecha_emision,
                "fecha_emision_examen_vih": res.fecha_emision_examen_vih,
                "numero_chequeo_vih": res.numero_chequeo_vih,
                "resultado_vih": res.resultado_vih,
                "proposito_examen": res.proposito_examen,
                "numero_ficha_aptitud": res.numero_ficha_aptitud,
                "observacion": res.observacion,
                "resultado_ficha": res.resultado_ficha,
                "restriccion": res.restriccion,
                "es_reconocimiento": True,
                })
            if certificado_medico:
                res.certificado_medico_id = certificado_medico.id
        return res

    @api.model
    def create(self, vals):
        vals["name"] = self._get_seq_with_company("reconocimiento_certificado_medico_code")
        res = super().create(vals)
        return res

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Documento persona must be unique.')
    ]
