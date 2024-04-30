# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError, UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tiempo_minimo_validez_documentos = fields.Integer(string="Tiempo mínimo de validez de documentos. (meses)")
    tiempo_maximo_validez_solicitudes = fields.Integer(string="Validez de la solicitudes (días)", default=3)
    libro_numero  = fields.Integer(string="Libro", default=0)
    sbu  = fields.Float(string="Salario Básico Unificado", default=450)

    estados_bloquean_naves_ids = fields.Many2many(
        'nave.nave.estado',
        string=_('Estados de Naves que impiden trámites'),
        help=_('Estados para las naves, que impiden estas se seleccionen en Órdenes de Venta y solicitudes'))

    #=== CRUD METHODS ===#

    def set_values(self):
        if self.tiempo_maximo_validez_solicitudes < 1:
            raise UserError(_("Los días de validez de las solicitudes no puede ser menor a cero."))
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('tramite.tiempo_minimo_validez_documentos', self.tiempo_minimo_validez_documentos)
        params.set_param('tramite.tiempo_maximo_validez_solicitudes', self.tiempo_maximo_validez_solicitudes)
        params.set_param('tramite.libro_numero', self.libro_numero)
        params.set_param('tramite.sbu', self.sbu)
        # self.env['ir.config_parameter'].set_param(
        #     'tramite.tiempo_minimo_validez_documentos', self.tiempo_minimo_validez_documentos)

        params.set_param('nave.estados_bloquean_naves_ids', self.estados_bloquean_naves_ids.ids)


    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            tiempo_minimo_validez_documentos=params.get_param('tramite.tiempo_minimo_validez_documentos'),
            tiempo_maximo_validez_solicitudes=params.get_param('tramite.tiempo_maximo_validez_solicitudes'),
            libro_numero=params.get_param('tramite.libro_numero'),
            sbu=params.get_param('tramite.sbu'),
        )

        estados_ids = params.get_param('nave.estados_bloquean_naves_ids')
        records = [(6, 0, literal_eval(estados_ids))] if estados_ids and literal_eval(estados_ids) else False
        res.update(
            estados_bloquean_naves_ids=records,
        )

        return res

