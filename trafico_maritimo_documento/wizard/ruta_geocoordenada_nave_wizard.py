from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class TraficoMaritimoInternacionalCostera(models.Model):
    _inherit = 'trafico.maritimo.internacional.costera'

    def button_ruta_geocoordenada_nave(self):
        self.ensure_one()
        ctx = dict(
            default_trafico_maritimo_internacional_costera_id = self.id,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("trafico_maritimo_documento.action_ruta_geocoordenada_nave_wizard")
        action.update({
            'context': ctx,
            })
        return action

class TraficoMaritimoArribo(models.Model):
    _inherit = 'trafico.maritimo.arribo'

    def button_ruta_geocoordenada_nave(self):
        self.ensure_one()
        ctx = dict(
            default_trafico_maritimo_arribo_id = self.id,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("trafico_maritimo_documento.action_ruta_geocoordenada_nave_wizard")
        action.update({
            'context': ctx,
            })
        return action

class TraficoMaritimoZarpe(models.Model):
    _inherit = 'trafico.maritimo.zarpe'

    def button_ruta_geocoordenada_nave(self):
        self.ensure_one()
        ctx = dict(
            default_trafico_maritimo_zarpe_id = self.id,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("trafico_maritimo_documento.action_ruta_geocoordenada_nave_wizard")
        action.update({
            'context': ctx,
            })
        return action

class RutaGeocoordenadaNaveWizard(models.TransientModel):
    _name = 'ruta.geocoordenada.nave.wizard'
    _description = 'Ruta Geocoordenada de la Nave Wizard'

    trafico_maritimo_internacional_costera_id = fields.Many2one('trafico.maritimo.internacional.costera', string=_('Trafico Maritimo Internacional Costera'))
    trafico_maritimo_arribo_id = fields.Many2one('trafico.maritimo.arribo', string=_('Trafico Maritimo Arribo'))
    trafico_maritimo_zarpe_id = fields.Many2one('trafico.maritimo.zarpe', string=_('Trafico Maritimo Zarpe'))

    trafico_maritimo_ruta_id = fields.Many2one(
        'trafico.maritimo.ruta',
        string=_('Tráfico Marítimo Ruta'),
        required=True)

    def action_ruta_geocoordenada_nave(self):
        self.ensure_one()
        trafico_maritimo = []
        if self.trafico_maritimo_internacional_costera_id:
            trafico_maritimo = self.trafico_maritimo_internacional_costera_id
        if self.trafico_maritimo_arribo_id:
            trafico_maritimo = self.trafico_maritimo_arribo_id
        if self.trafico_maritimo_zarpe_id:
            trafico_maritimo = self.trafico_maritimo_zarpe_id
        rutas = []
        rutas_geocoordenadas = self.trafico_maritimo_ruta_id.ruta_geocoordenada_ids
        if rutas_geocoordenadas:
            for r in rutas_geocoordenadas:
                rutas.append((0, 0, {
                    "orden": r.orden,
                    "latitud": r.latitud,
                    "latitud_dms": r.latitud_dms,
                    "longitud": r.longitud,
                    "longitud_dms": r.longitud_dms,
                    "ultimo_evento": 'P',
                    # "rumbo": r.rumbo,
                    # "velocidad": r.velocidad,
                    #"fecha": False
                }))
        trafico_maritimo.sudo().write({
            'ruta_ids': rutas,
        })
        return True
