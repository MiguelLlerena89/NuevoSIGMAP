from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class TraficoMaritimoNavegacion(models.Model):
    _inherit = 'trafico.maritimo.navegacion'

    @api.depends('nave_id')
    def _compute_dotacion_minina_nave(self):
        for rec in self:
            if rec.nave_id:
                if len(rec.nave_id.dotacion_minima_jerarquia_ids) == 0 and rec.nave_id.tipo == 'NAC':
                    raise ValidationError('La nave no tiene una dotación mínima')
                if rec.nave_id.dotacion_minima_jerarquia_ids:
                    crew_list_line_ids_commands = [Command.clear()]
                    default_dotacion_minina_nave = rec.nave_id.dotacion_minima_jerarquia_ids
                    for dotacion in default_dotacion_minina_nave:
                        crew_list_line_ids_commands += [Command.create({
                            'jerarquia_plaza_id': dotacion.jerarquia_id.id,
                            'personal_maritimo_id': False,
                            'numero_libretin': '',
                            'obligatorio': True,
                        }) for numero in range(dotacion.number)]
                    rec.crew_list_ids = crew_list_line_ids_commands
            # else:
            #     raise ValidationError('No existe nave asociada.')

    #OMI CREW LIST
    crew_list_ids = fields.One2many(
        'trafico.maritimo.crews.list',
        'trafico_maritimo_navegacion_id',
        string=_("Tráfico Marítimo Dotación"),
        compute='_compute_dotacion_minina_nave',
        store=True,
        readonly=False,
    )

class TraficoMaritimoCrewList(models.Model):
    _name = 'trafico.maritimo.crews.list'
    _description = "Dotación"

    @api.depends('jerarquia_plaza_id')
    def _get_jerarquia_personal_maritimo_ids(self):
        permar_ids = []
        if self.jerarquia_plaza_id:
            domain = [
                #('company_id', '=', self.company_id.id),
                ('jerarquia_id','=', self.jerarquia_plaza_id.id),
                ('active','=', True),
            ]
            permar_ids = self.env['personal.maritimo.jerarquia'].search(domain).mapped('personal_maritimo_id').ids
            print(permar_ids)
        return permar_ids #[('id', 'in', permar_ids)]

    @api.onchange("jerarquia_plaza_id")
    def _onchange_jerarquia_plaza_id(self):
        permar_ids = self._get_jerarquia_personal_maritimo_ids()
        return {'domain': {'personal_maritimo_id': [('id', 'in', permar_ids)]}}

    def _get_domain_personal_maritimo(self):
        print(self.jerarquia_plaza_id)
        permar_ids = self._get_jerarquia_personal_maritimo_ids()
        return [('id', 'in', permar_ids)]

    trafico_maritimo_navegacion_id = fields.Many2one('trafico.maritimo.navegacion', string=_("Tráfico Marítimo Navegación"), ondelete='cascade', index=True, copy=False)
    nave_id = fields.Many2one(related='trafico_maritimo_navegacion_id.nave_id', string=_('Nave'), store=True, tracking=True)
    #nave_tipo_id = fields.Many2one(related='nave_id.nave_tipo_id', string=_('Tipo Nave'), store=True, tracking=True)
    reparto_origen_id = fields.Many2one(related='trafico_maritimo_navegacion_id.reparto_origen_id', string=_('Reparto Origen'), tracking=True)
    reparto_final_id = fields.Many2one(related='trafico_maritimo_navegacion_id.reparto_final_id', string=_('Reparto Destino'), tracking=True)
    puerto_origen_id = fields.Many2one(related='trafico_maritimo_navegacion_id.puerto_origen_id', string=_('Puerto Origen'), tracking=True)
    puerto_destino_id = fields.Many2one(related='trafico_maritimo_navegacion_id.puerto_destino_id', string=_('Puerto Destino'), tracking=True)

    fecha_origen = fields.Datetime(related='trafico_maritimo_navegacion_id.fecha_origen', string=_('Fecha Origen'), tracking=True)
    fecha_destino = fields.Datetime(related='trafico_maritimo_navegacion_id.fecha_destino', string=_('Fecha Destino'), tracking=True)

    ultimo_evento = fields.Selection(related='trafico_maritimo_navegacion_id.ultimo_evento', string=_('Evento'))
    jerarquia_plaza_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string=_("Plaza"), tracking=True)
    personal_maritimo_id = fields.Many2one('personal.maritimo', string=_('Personal Marítimo'),
        #domain = "[('jerarquia_id', '=', jerarquia_plaza_id)]",
        #domain = _get_domain_personal_maritimo,
        tracking=True)
    jerarquia_id = fields.Many2one(related='personal_maritimo_id.jerarquia_id', string=_("Jerarquía"), store=True, tracking=True)
    nationality = fields.Char(related='personal_maritimo_id.nationality', string=_('Nationality'), readonly=True, tracking=True)
    birthday = fields.Date(related='personal_maritimo_id.birthday', string=_('Date of Birth'), readonly=True, tracking=True)
    numero_libretin = fields.Char(string=_('Seaman Book'))
    obligatorio = fields.Boolean(string='Dotación Mínima?', default=False, readonly=True)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_obligatorio(self):
        for rec in self:
            if rec.obligatorio:
                raise UserError(_('No puede eliminar esta plaza porque pertence a la dotación mínima.'))