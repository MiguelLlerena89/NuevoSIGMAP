from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = ['personal.maritimo']

    arribos_ids = fields.One2many(
        'trafico.maritimo.crews.list', 'personal_maritimo_id', string='Arribos')
    arribo_count = fields.Integer(compute='_compute_arribo_count')

    def _compute_arribo_count(self):
        for tripulacion in self:
            tripulacion.arribo_count = len(tripulacion.arribos_ids.filtered(lambda z: z.ultimo_evento == 'A'))

    def action_open_arribos(self):
        self.ensure_one()
        return {
            'name': 'Personal Marítimo en Arribos',
            'type': 'ir.actions.act_window',
            'res_model': 'trafico.maritimo.crews.list',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('trafico_maritimo_documento.view_trafico_maritimo_crews_list_tree').id, 'tree'), (False, 'form')],
            'domain': [('id', 'in', self.arribos_ids.ids),('ultimo_evento','=','A')],
            'context':  {'default_personal_maritimo_id': self.id,'default_ultimo_evento': 'A'}
        }


class TraficoMaritimoArribo(models.Model):
    _name = 'trafico.maritimo.arribo'
    _description = 'Tráfico Marítimo Arribo'
    _inherit = "trafico.maritimo.documento.base"

    #Combustible
    remanente = fields.Float('Remante')

    def action_validar(self):
        self.validar()

    def validar(self):
        msg = ''
        if self.nave_id.lista_autorizada !='0':
            msg = msg + _('La nave %s no esta en lista autorizada, no puede continuar el proceso.\n') % (self.nave_id.name)
        if self.tipo == 'NAC' and self.es_primera_vez:
            msg = msg + _('Debe ingresar un zarpe inicial para la nave %s.\n') % (self.nave_id.name)
        if not self.reparto_origen_id:
            msg = msg + 'Debe registrar jurisdicción arribo.\n'
        # if not self.reparto_final_id:
        #     msg = msg + 'Debe registrar próxima jurisdicción.\n'
        # if not self.puerto_origen_id:
        #     msg = msg + 'Debe registrar puerto arribo.\n'
        # if not self.puerto_destino_id:
        #     msg = msg + 'Debe registrar próximo puerto.\n'
        # if not self.crew_list_ids:
        #     msg = msg + 'Debe registrar listado de la tripulación.\n'
        if msg:
            raise ValidationError(_(msg))
        return True

    def action_generar_documento(self):
        self.state = "vigente"
        if self.tipo == 'NAC' and self.ultimo_evento == 'A':
            msg = "Se ha impreso el Documento de Arribo Nacional No. %s " % (self.name_get()[0][1])
            self.message_post(body=msg)
            #return self.env.ref('trafico_maritimo_documento.action_report_documento_arribo').report_action(self)
        if self.tipo == 'INT' and self.ultimo_evento == 'A':
            msg = "Se ha impreso el Documento de Arribo Internacional No. %s " % (self.name_get()[0][1])
            self.message_post(body=msg)
            #return self.env.ref('trafico_maritimo_documento.action_report_documento_arribo').report_action(self)
        return super().action_generar_documento()