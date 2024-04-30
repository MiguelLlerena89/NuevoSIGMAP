from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class TraficoMaritimoRutaGeocoordenada(models.Model):
    _inherit = 'trafico.maritimo.ruta.geocoordenada'

    def button_genera_coordenada(self):
        self.ensure_one()
        ctx = dict(
            default_trafico_maritimo_ruta_id = self.id,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("trafico_maritimo.action_registrar_posicion_coordenada_wizard")
        action.update({
            'context': ctx,
            })
        return action

class RegistrarPosicionCoordenadaWizard(models.TransientModel):
    _name = 'registrar.posicion.coordenada.wizard'
    _description = 'Registrar Posiciones Coordenadas Wizard'

    trafico_maritimo_ruta_id = fields.Many2one(
        'trafico.maritimo.ruta.geocoordenada',
        string=_('Tráfico Marítimo Ruta Geocoordenada'),
        readonly=True,
        tracking=True)

    latitud_grado = fields.Integer('Grado', size=2, required=True)
    latitud_minuto = fields.Integer('Minuto', required=True)
    latitud_segundo = fields.Integer('Segundo', required=True)
    punto_cardinal_latitud = fields.Selection([('N', 'N'),('S', 'S')], string='Tipo Latitud', default="N")

    longitud_grado = fields.Integer('Grado', required=True)
    longitud_minuto = fields.Integer('Minuto', required=True)
    longitud_segundo = fields.Integer('Segundo', required=True)
    punto_cardinal_longitud = fields.Selection([('W', 'W'),('E', 'E')], string='Tipo Longitud', default="W")

    latitud = fields.Float(string='Latitud', digits=(10, 7), compute='_compute_coordenadas_decimales', readonly=True)
    longitud = fields.Float(string='Longitud', digits=(10, 7), compute='_compute_coordenadas_decimales', readonly=True)
    latitud_dms = fields.Char(string='Latitud DMS', compute='_compute_coordenadas', readonly=True)
    longitud_dms = fields.Char(string='Longitud DMS', compute='_compute_coordenadas', readonly=True)

    @api.depends('latitud_grado','latitud_minuto','latitud_segundo','punto_cardinal_latitud','longitud_grado','longitud_minuto','longitud_segundo','punto_cardinal_longitud')
    def _compute_coordenadas_decimales(self):
        for rec in self:
            # if rec.latitud != 0 and rec.latitud_grado == 0 and rec.latitud_minuto == 0 and rec.latitud_segundo == 0:
            #     rec.latitud_grado, rec.latitud_minuto, rec.latitud_segundo, rec.punto_cardinal_latitud = self._convertir_a_coordenadas(rec.latitud, 'latitud')
            # if rec.longitud != 0 and rec.longitud_grado == 0 and rec.longitud_minuto == 0 and rec.longitud_segundo == 0:
            #     rec.longitud_grado, rec.longitud_minuto, rec.longitud_segundo, rec.punto_cardinal_longitud = self._convertir_a_coordenadas(rec.longitud, 'longitud')
            rec.latitud = self._convertir_a_decimal(self.latitud_grado, self.latitud_minuto, self.latitud_segundo, self.punto_cardinal_latitud)
            rec.longitud = self._convertir_a_decimal(self.longitud_grado, self.longitud_minuto, self.longitud_segundo, self.punto_cardinal_longitud)

    def _convertir_a_decimal(self, grados, minutos, segundos, punto_cardinal):
        value = grados + minutos / 60 + segundos / 3600
        result = -1*value if punto_cardinal in ['S','W'] else value
        return result

    def _convertir_a_coordenadas(self, coordenada_decimal, punto_cardinal):
        grados = int(coordenada_decimal)
        minutos = int((coordenada_decimal - grados) * 60)
        segundos = ((coordenada_decimal - grados) * 60 - minutos) * 60
        if punto_cardinal == 'latitud':
            direction = 'N' if coordenada_decimal >= 0 else 'S'
        else:
            direction = 'E' if coordenada_decimal >= 0 else 'W'
        return grados, minutos, segundos, direction

    @api.depends('latitud', 'longitud')
    def _compute_coordenadas(self):
        # def decdeg2dms(dd, direction='x'):
        #     try:
        #         dd = float(dd)
        #     except ValueError:
        #         return None

        #     if dd < 0:
        #         appendix = 'W' if direction == 'x' else 'S'
        #     else:
        #         appendix = 'E' if direction == 'x' else 'N'
        def decdeg2dms(dd, direction):
            try:
                dd = float(dd)
            except ValueError:
                return None

            if direction == 'lat':
                appendix = 'S' if dd < 0 else 'N'
            else:
                appendix = 'W' if dd < 0 else 'E'
            is_positive = dd >= 0
            dd = abs(dd)
            minutes, seconds = divmod(dd * 3600, 60)
            degrees, minutes = divmod(minutes, 60)
            #degrees = degrees if is_positive else -degrees
            return (round(degrees), round(minutes), round(seconds), appendix)

        for rec in self:
            if not rec.latitud:
                rec.latitud_dms = ''
            else:
                if rec.latitud != 0 and rec.latitud_grado == 0 and rec.latitud_minuto == 0 and rec.latitud_segundo == 0:
                    rec.latitud_grado, rec.latitud_minuto, rec.latitud_segundo, rec.punto_cardinal_latitud = self._convertir_a_coordenadas(rec.latitud, 'latitud')
                    print('latitud......')
                lat = decdeg2dms(rec.latitud,'lat')
                print('lat....', lat)
                if not lat:
                    rec.latitud_dms = ''
                else:
                    rec.latitud_dms = f"{lat[0]}° {lat[1]}' {lat[2]}'' {rec.punto_cardinal_latitud}" #{lat[3]}

            if not rec.longitud:
                rec.longitud_dms = ''
            else:
                if rec.longitud != 0 and rec.longitud_grado == 0 and rec.longitud_minuto == 0 and rec.longitud_segundo == 0:
                    rec.longitud_grado, rec.longitud_minuto, rec.longitud_segundo, rec.punto_cardinal_longitud = self._convertir_a_coordenadas(rec.longitud, 'longitud')
                    print('longitud......')
                lon = decdeg2dms(rec.longitud,'lon')
                print('lon....', lon)
                if not lon:
                    rec.longitud_dms = ''
                else:
                    rec.longitud_dms = f"{lon[0]}° {lon[1]}' {lon[2]}'' {rec.punto_cardinal_longitud}" #{lat[3]}

    def action_registrar_posicion_coordenada_nave(self):
        self.ensure_one()
        #self._check_coordenadas()
        #trafico_maritimo_coordenadas = self.trafico_maritimo_ruta_id if self.trafico_maritimo_ruta_id else []
        if self.trafico_maritimo_ruta_id:
            self.trafico_maritimo_ruta_id.sudo().write({
                'latitud': self.latitud,
                'longitud': self.longitud,
                'latitud_dms': self.latitud_dms,
                'longitud_dms': self.longitud_dms,
            })
        return True
