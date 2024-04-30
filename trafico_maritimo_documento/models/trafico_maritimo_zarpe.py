from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ['personal.maritimo']

    zarpes_ids = fields.One2many(
        'trafico.maritimo.crews.list', 'personal_maritimo_id', string='Zarpes')
    zarpe_count = fields.Integer(compute='_compute_zarpe_count')

    def _compute_zarpe_count(self):
        for tripulacion in self:
            tripulacion.zarpe_count = len(tripulacion.zarpes_ids.filtered(lambda z: z.ultimo_evento == 'Z'))

    def action_open_zarpes(self):
        self.ensure_one()
        return {
            'name': 'Personal Marítimo en Zarpes',
            'type': 'ir.actions.act_window',
            'res_model': 'trafico.maritimo.crews.list',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('trafico_maritimo_documento.view_trafico_maritimo_crews_list_tree').id, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.zarpes_ids.ids),('ultimo_evento','=','Z')],
            'context':  {'default_personal_maritimo_id': self.id,'default_ultimo_evento': 'Z'}
        }

class TraficoMaritimoZarpe(models.Model):
    _name = 'trafico.maritimo.zarpe'
    _description = 'Tráfico Marítimo Zarpe'
    _inherit = "trafico.maritimo.documento.base"

    #Combustible
    volumen = fields.Float('Volumen')
    guia_remision = fields.Char('Guía de Remisión')
    combustible_nave = fields.Float('Combustible Nave')
    combustible_fibra = fields.Float('Combustible Fibras')

    def action_validar(self):
        self.validar()

    def validar(self):
        msg = ''
        if self.nave_id.lista_autorizada !='0':
            msg = msg + _('La nave %s no esta en lista autorizada, no puede continuar el proceso.\n') % (self.nave_id.name)
        if self.nave_id.tipo =='NAC' and self.es_primera_vez:
            msg = msg + _('Debe ingresar un arribo inicial para la nave %s.\n') % (self.nave_id.name)
        if not self.reparto_origen_id:
            msg = msg + 'Debe registrar jurisdicción arribo.\n'
        if not self.reparto_final_id:
            msg = msg + 'Debe registrar próxima jurisdicción.\n'
        if not self.puerto_origen_id:
            msg = msg + 'Debe registrar puerto zarpe.\n'
        if not self.puerto_destino_id:
            msg = msg + 'Debe registrar próximo puerto.\n'
        if not self.crew_list_ids:
            msg = msg + 'Debe registrar listado de tripulación.\n'
        if msg:
            raise ValidationError(_(msg))
        return True

    @api.onchange("nave_id")
    def _onchange_nave_id(self):
        if self.nave_id:
            if self.nave_id.lista_autorizada !='0':
                raise ValidationError(_('La nave %s no esta en lista autorizada, no puede continuar el proceso.') % (self.nave_id.name))
            motors = []
            for m in self.nave_id.motors_ids.filtered(lambda a: a.active):
                motors.append((0, 0, {
                    "nave_id": m.id,
                    "codigo_motor": m.codigo_motor,
                    "codigo_troquelado": m.codigo_troquelado,
                    "tipo_marca": m.tipo_marca,
                    "tipo_motor": m.tipo_motor,
                    "serie": m.serie,
                    "modelo": m.modelo,
                    "velocidad": m.velocidad,
                    "potencia": m.potencia,
                    "propietario": m.propietario,
                    "active": m.active,
                }))
            self.write({
                "motors_zarpe_ids": motors,
                })
        else:
            if self.motors_zarpe_ids:
                self.write({"motors_zarpe_ids": [(5,0,0)]})

    def create_arribo_navegacion_nueva_nave(self, vals):
        evento_reverso, model_inverso = self._get_evento_inverso_navegacion(vals.get('ultimo_evento'))
        try:
            data = {
                'nave_id': vals.get('nave_id'),
                'company_id': vals.get('company_id'),
                'documento_emitido_id': vals.get('documento_emitido_id'), #vals.get('id'),
                'ultimo_evento': evento_reverso,
                'tipo': vals.get('tipo'),
                'tipo_trafico_id': vals.get('tipo_trafico_id'),
                'reparto_origen_id': vals.get('reparto_origen_id'),
                'reparto_final_id': vals.get('reparto_origen_id'),
                'puerto_origen_id': False, #reg.puerto_origen_id,
                'puerto_destino_id': False, #reg.puerto_destino_id,
                'observacion': 'Arribo generado automáticamente por el sistema porque la nave no tiene navegación.',
                #'state': 'ARRIBO',
            }
            print(data)
            trafico_maritimo = self.env[model_inverso].create(data)
            print("trafico maritimo inverso... ",str(trafico_maritimo))

        except Exception as e:
            raise ValidationError(_(e))
        return True

    def action_generar_documento(self):
        self.state = "vigente"
        if self.tipo == 'NAC' and self.ultimo_evento == 'Z':
            msg = "Se ha impreso el Documento de Zarpe Nacional No. %s " % (self.name_get()[0][1])
            self.message_post(body=msg)
            #return self.env.ref('trafico_maritimo_documento.action_report_documento_zarpe').report_action(self)
        if self.tipo == 'INT' and self.ultimo_evento == 'Z':
            msg = "Se ha impreso el Documento de Zarpe Internacional No. %s " % (self.name_get()[0][1])
            self.message_post(body=msg)
            #return self.env.ref('trafico_maritimo_documento.action_report_documento_zarpe_internacional').report_action(self)
        return super().action_generar_documento()