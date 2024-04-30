from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    #_description = 'Parámetros Ws SRI'

    AMBIENTE_PRUEBAS = '1'
    AMBIENTE_PRODUCCION = '2'

    recepcion_wsdl = {
        AMBIENTE_PRUEBAS: 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl',
        AMBIENTE_PRODUCCION: 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl',
    }

    autorizacion_wsdl = {
        AMBIENTE_PRUEBAS: 'https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl',
        AMBIENTE_PRODUCCION: 'https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl',
    }
    # check ambiente compania
    ambiente = fields.Selection(
        [
            ('1', 'Pruebas'),
            ('2', 'Producción')
        ],
        string='Tipo de Ambiente',
        required=True,
        default="1"
    )
    name = fields.Char(string="Ambiente")
    sri_url_recepcion = fields.Char(string="Recepción wsdl")
    sri_url_autorizacion = fields.Char(string="Autorización wsdl")
    sri_url_recepcion_pruebas = fields.Char(string="Recepción wsdl pruebas")
    sri_url_autorizacion_pruebas = fields.Char(string="Autorización wsdl pruebas")
    sri_clave_acceso_size = fields.Integer(string="Longitud clave acceso", help="Ingrese longitud clave acceso")

    #=== CRUD METHODS ===#

    def set_values(self):
        if self.sri_clave_acceso_size < 0:
            raise UserError(_("Clave de acceso debe ser mayor a 0."))
        super().set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param('l10n_ec_sri.sri_url_autorizacion', self.sri_url_autorizacion)
        params.set_param('l10n_ec_sri.sri_url_recepcion', self.sri_url_recepcion)
        params.set_param('l10n_ec_sri.sri_url_autorizacion_pruebas', self.sri_url_autorizacion_pruebas)
        params.set_param('l10n_ec_sri.sri_url_recepcion_pruebas', self.sri_url_recepcion_pruebas)
        params.set_param('l10n_ec_sri.sri_clave_acceso_size', self.sri_clave_acceso_size)

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            sri_url_autorizacion=params.get_param('l10n_ec_sri.sri_url_autorizacion'),
            sri_url_recepcion=params.get_param('l10n_ec_sri.sri_url_recepcion'),
            sri_url_autorizacion_pruebas=params.get_param('l10n_ec_sri.sri_url_autorizacion_pruebas'),
            sri_url_recepcion_pruebas=params.get_param('l10n_ec_sri.sri_url_recepcion_pruebas'),
            sri_clave_acceso_size=params.get_param('l10n_ec_sri.sri_clave_acceso_size'),
        )
        return res


