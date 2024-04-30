from odoo import api, fields, models, _, Command
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)

class TraficoMaritimoDocumentoBase(models.AbstractModel):
    _name = 'trafico.maritimo.documento.base'
    _description = 'Documento Base de Tráfico Marítimo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'trafico.maritimo.navegacion': 'trafico_maritimo_navegacion_id', 'tramite.documento.emitido': 'documento_emitido_id'}
    _rec_names_search = ['name', 'ultimo_evento', 'tipo_trafico']  # TODO vat must be sanitized the same way for storing/searching
    _check_company_auto = True

    def _default_company(self):
        return self.env.user.company_id

    trafico_maritimo_navegacion_id = fields.Many2one('trafico.maritimo.navegacion', ondelete='restrict', auto_join=True, index=True, store=True,
        string='Tráfico Marítimo Navegación relacionado', help='Información relacionada de tráfico marítimo')

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)
    user_id = fields.Many2one(
        'res.users', string='Usuario', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    documento_emitido_id = fields.Many2one(
        "tramite.documento.emitido",
        string=_("Documento emitido"),
        ondelete='cascade',
        tracking=True)
    name = fields.Char(string=_("Nombre"), size=100, index=True, tracking=True)
    numero = fields.Char(string=_("Numero"), size=100, index=True, tracking=True)

    numero_formato = fields.Integer(string="Número de Formato", tracking=True)
    #observacion = fields.Html('Observaciones')
    active = fields.Boolean(string=_('Active?'), default=True)

    es_primera_vez = fields.Boolean(string=_('Por Primera Vez'),
                                    compute='_compute_por_primera_vez',
                                    default=False,
                                    tracking=True)

    @api.depends('nave_id')
    def _compute_por_primera_vez(self):
        for rec in self:
            if rec.nave_id:
                domain = [
                    ('nave_id','=', rec.nave_id.id),
                    ('ultimo_evento','!=', self.ultimo_evento)
                ]
                nave_nueva = self.env["trafico.maritimo.navegacion"].search(domain, limit=1)
                rec.es_primera_vez = bool(nave_nueva) #True if not nave_nueva else False
            else:
                rec.es_primera_vez = False

    def _get_seq_with_company(self, code):
        return '%s-%s' % (self.env.user.company_id.name, self.env["ir.sequence"].next_by_code(code))

    def _get_seq_with_reparto(self, siglas, code):
        return '%s-%s' % (siglas, self.env["ir.sequence"].next_by_code(code))

    # def action_pendiente(self):
    #     self.write({'state': 'pendiente'})

    # def action_validar(self):
    #     self.valida_documento()
    #     self.write({'state': 'validado'})

    def action_caducar(self):
        self.write({'state': 'caducado'})

    def action_anular(self):
        self.write({'state': 'anulado'})

    def validar(self):
        pass

    def action_generar_documento(self):
        self.validar()
        self.documento_emitido_id.action_generar_documento()

    def write(self, vals):
        res = super().write(vals)
        return res

    def _get_rutas(self, obj_prenavegacion):
        list_coordenadas = []
        listado_rutas = obj_prenavegacion.ruta_ids
        if listado_rutas:
            for r in listado_rutas:
                list_coordenadas.append((0, 0, {
                    "orden": r.orden,
                    "latitud": r.latitud,
                    "longitud": r.longitud,
                    "latitud_dms": r.latitud_dms,
                    "longitud_dms": r.longitud_dms,
                    "ultimo_evento": r.ultimo_evento,
                    "rumbo": r.rumbo,
                    "velocidad": r.velocidad,
                    "fecha": r.fecha
                }))
            if obj_prenavegacion.ultimo_evento == 'F':
                list_coordenadas.append((0, 0, {
                    "orden": 0,
                    "latitud": obj_prenavegacion.latitud,
                    "longitud": obj_prenavegacion.longitud,
                    "latitud_dms": obj_prenavegacion.latitud_dms,
                    "longitud_dms": obj_prenavegacion.longitud_dms,
                    "ultimo_evento": 'QTH',
                    "rumbo": obj_prenavegacion.rumbo,
                    "velocidad": obj_prenavegacion.velocidad,
                    "fecha": obj_prenavegacion.fecha_hora_qth
                }))
        return list_coordenadas

    def _get_dotacion(self, objIAA):
        list_dotacion = []
        if objIAA:
            if len(objIAA.crew_list_ids) > 0:
                crew_list_line_ids_commands = [Command.clear()]
                crew_list_line_ids_commands += [Command.create({
                    'personal_maritimo_id': dotacion.personal_maritimo_id.id,
                    'jerarquia_plaza_id': dotacion.personal_maritimo_id.jerarquia_id.id,
                    'numero_libretin': dotacion.numero_libretin,
                    'obligatorio': True,
                }) for dotacion in objIAA.crew_list_ids]
                list_dotacion = crew_list_line_ids_commands
            else:
                raise ValidationError('Formato IAA no tiene dotación definida.')
        return list_dotacion

    def _get_carga(self, objIAA):
        list_carga = []
        if objIAA:
            if len(objIAA.cargo_ids) > 0:
                carga_list_line_ids_commands = [Command.clear()]
                carga_list_line_ids_commands += [Command.create({
                    'bookin_no': carga.bookin_no,
                    'container_no': carga.container_no,
                    'package_type': carga.package_type,
                    'gross_weight': carga.gross_weight,
                    'measurement': carga.measurement,
                }) for carga in objIAA.cargo_ids]
                list_carga = carga_list_line_ids_commands
            else:
                raise ValidationError('Formato IAA no tiene carga definida.')
        return list_carga

    def _get_pasajeros(self, objIAA):
        list_pasajeros = []
        if objIAA:
            if len(objIAA.passengers_list_ids) > 0:
                passengers_list_line_ids_commands = [Command.clear()]
                passengers_list_line_ids_commands += [Command.create({
                    'personal_maritimo_id': pasajero.personal_maritimo_id.id,
                    'port_embarkation_id': pasajero.port_embarkation_id.id,
                    'port_disembarkation_id': pasajero.port_disembarkation_id.id,
                    'passeger_trafic': pasajero.passeger_trafic,
                }) for pasajero in objIAA.passengers_list_ids]
                list_pasajeros = passengers_list_line_ids_commands
            # else:
            #     raise ValidationError('Formato IAA no tiene lista de pasajeros.')
        return list_pasajeros

    def _prepare_trafico_maritimo_navegacion(self, vals):
        return {
            'company_id': vals["company_id"],
            'nave_id': vals['nave_id'],
            'reparto_origen_id': vals['reparto_origen_id'],
            'fecha_origen': vals['fecha_origen'],
            'reparto_final_id': vals['reparto_final_id'] if 'reparto_final_id' in vals else False,
            'fecha_destino': vals['fecha_destino'] if 'fecha_destino' in vals else False,
            'ultimo_evento': vals['ultimo_evento'],
            'tipo_trafico_id': vals['tipo_trafico_id'],
            'tipo': vals['tipo'],
            #'ruta_ids': vals['ruta_ids'],
            'name': vals["name"],
        }

    @api.model
    def create(self, vals):
        res = []
        if 'documento_emitido_id' in vals:
            doc = self.env['tramite.documento.emitido'].browse(vals['documento_emitido_id'])
            model = doc.model_model
            ultimo_evento = doc.tramite_id.ultimo_evento
            siglas = doc.reparto_origen_id.siglas
            if not siglas:
                raise ValidationError('Debe definir el siglas del reparto o juridicción')
            if model in ['trafico.maritimo.arribo', 'trafico.maritimo.zarpe']:
                vals["company_id"] = doc.company_id.id
                vals["nave_id"] = doc.nave_id.id
                vals["reparto_origen_id"] = doc.reparto_origen_id.id
                vals["fecha_origen"] = doc.fecha_origen
                if doc.reparto_final_id.id:
                    vals["reparto_final_id"] = doc.reparto_final_id.id
                if doc.fecha_destino:
                    vals["fecha_destino"] = doc.fecha_destino
                vals["ultimo_evento"] = doc.tramite_id.servicio_id.ultimo_evento
                vals["tipo_trafico_id"] = doc.tramite_id.servicio_id.tipo_trafico_id.id
                vals["tipo"] = doc.tramite_id.servicio_id.tipo_trafico_id.tipo
                if doc.tramite_id.trafico_maritimo_prenavegacion_id:
                    vals['puerto_origen_id'] = doc.tramite_id.trafico_maritimo_prenavegacion_id.puerto_origen_id.id
                    if doc.tramite_id.trafico_maritimo_prenavegacion_id.puerto_destino_id:
                        vals['puerto_destino_id'] = doc.tramite_id.trafico_maritimo_prenavegacion_id.puerto_destino_id.id
                    vals["ruta_ids"] = self._get_rutas(doc.tramite_id.trafico_maritimo_prenavegacion_id)
                    vals["crew_list_ids"] = self._get_dotacion(doc.tramite_id.trafico_maritimo_prenavegacion_id.trafico_maritimo_iaa_id)
                    vals["cargo_ids"] = self._get_carga(doc.tramite_id.trafico_maritimo_prenavegacion_id.trafico_maritimo_iaa_id)
                    vals["passengers_list_ids"] = self._get_pasajeros(doc.tramite_id.trafico_maritimo_prenavegacion_id.trafico_maritimo_iaa_id)
                sequence_code = "documento_trafico_maritimo_permiso_arribo_code" if ultimo_evento == 'A' else "documento_trafico_maritimo_permiso_zarpe_code"
                vals["name"] = self._get_seq_with_reparto(siglas,sequence_code)
                vals["fecha_inicio"] = doc.fecha_inicio
                vals["fecha_caducidad"] = doc.fecha_caducidad
                vals["trafico_maritimo_navegacion_id"] = self.env['trafico.maritimo.navegacion'].create(self._prepare_trafico_maritimo_navegacion(vals)).id
        print(vals)
        #return super().create(vals)
        res = super().create(vals)
        if res.nave_id:
            estado_navegacion = 'prearribo' if ultimo_evento == 'A' else 'prezarpe'
            res.nave_id.sudo().write({'estado_navegacion': estado_navegacion})