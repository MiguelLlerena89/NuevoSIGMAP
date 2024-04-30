import base64
import json

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, time
from dateutil.relativedelta import relativedelta

class NaveDocumentoOficio(models.Model):
    _name = 'nave.documento.oficio'
    _description = 'Documento Oficio'
    _inherit = "nave.documento.base"

    READONLY_STATES = { state: [('readonly', True)] for state in {'vigente', 'caducado', 'anulado'}}

    asunto = fields.Char(string='Asunto', index=True, copy=False, tracking=True, states=READONLY_STATES)
    #dedicado = fields.Char(string='Dedicado', index=True, copy=False, tracking=True, states=READONLY_STATES)
    descripcion = fields.Html(string='Descripción', index=True, copy=False, tracking=True,states=READONLY_STATES)

    tipo_oficio = fields.Selection([
        ('cuadro_zafarrancho', 'Cuadro de Zafarrancho'),
        ('inf_tec_fav', _('Informe Técnico Favorable - Importacion/Nacionalización de Naves')),
        ('contr_fleta', _('Contrato de Fletamento')),
        ('contr_fleta_casco', _('Contrato de Fletamento a Casco desnudo')),
        ('contr_fleta_explo', _('Contrato de Fletamento por Exploración')),
        ('contr_asoci', _('Contrato de Asociación')),
        ('contr_int_temp', _('Contrato por Internación Temporal')),
        ('inf_tec_fav_contr', _('Informe Técnico Favorable - Naves con contrato de fletamento, asociación o arrendamiento')),
        ('rector_puerto', _('Supervisión Rector del Puerto')),
    ], string='Tipo Oficio', index=True, copy=False, tracking=True)

    def validar(self):
        msg = ''
        if not self.asunto:
            msg = msg + 'Debe definir el asunto del oficio.\n'
        if not self.descripcion:
            msg = msg + 'Debe definit texto de la descripción del oficio.\n'
        if msg:
            raise ValidationError(_(msg))
        return True

    @api.model
    def create(self, vals):
        code = ''
        tipo = ''
        documento_emitido_id = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
        servicio = documento_emitido_id.tramite_id.servicio_id
        if servicio.id == self.env.ref("tramite.tramite_documento_110").id:
            code = "documento_cuadro_zafarrancho_code"
            tipo = 'cuadro_zafarrancho'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_inf_tec_fav").id:
            code = 'documento_inf_tec_fav_code'
            tipo = 'inf_tec_fav'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_fleta").id:
            code = 'documento_contrato_fletamento_code'
            tipo = 'contr_fleta'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_fleta_casco").id:
            code = 'documento_contr_fleta_casco_code'
            tipo = 'contr_fleta_casco'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_fleta_explo").id:
            code = 'documento_contr_fleta_explo_code'
            tipo = 'contr_fleta_explo'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_asoci").id:
            code = 'documento_contrato_asociacion_code'
            tipo = 'contr_asoci'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_contr_int_temp").id:
            code = 'documento_contr_int_temp_code'
            tipo = 'contr_int_temp'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_inf_tec_fav_contr").id:
            code = 'documento_inf_tec_fav_contr_code'
            tipo = 'inf_tec_fav_contr'
        if servicio.id == self.env.ref("nave_documento.tramite_documento_nave_rector_puerto").id:
            code = 'documento_rector_puerto_code'
            tipo = 'rector_puerto'

        if len(code) == 0:
            raise ValidationError(_('No existe secuencial para ese servicio.'))
        vals["tipo_oficio"] = tipo
        vals["es_oficio"] = True
        vals["name"] = 'ARE-' + self._get_seq_with_company(code) + '-O' #'Oficio Nro. ARE-' + self._get_seq_with_company(code) + '-O'
        return super().create(vals)

    _sql_constraints = [
        ('documento_oficio_uniq', 'unique (documento_emitido_id)', ('El oficio para la nave debe ser único.'))
    ]