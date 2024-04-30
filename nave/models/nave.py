from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)

class Nave(models.Model):
    _name = 'nave.nave'
    _description = _( 'Ship')
    _inherit = ['mail.thread', 'mail.activity.mixin', 'sigmap.updated.by']

    # Bandera Pais
    bandera_pais_id = fields.Many2one(
        'res.country',
        ondelete='restrict',
        string=_('Bandera País'),
        required=True,
        copy=False,
        tracking=True)

    # Numero OMI
    omi_number = fields.Char(
        string=_('Número OMI'),
        required=False,
        index=True,
        copy=False,
        tracking=True)

    # Matricula
    matricula = fields.Char(
        string=_('Matrícula'),
        required=False,
        index=True,
        copy=False,
        tracking=True)

    # Puerto Registro
    """
    puerto_registro_id = fields.Many2one(
        'sigmap.puerto.registro',
        ondelete='restrict',
        string=_('Registry Port'),
        required=True,
        copy=False,
        tracking=True)
    """

    # Puerto Registro
    reparto_id = fields.Many2one(
        'sigmap.reparto',
        ondelete='restrict',
        string=_('Puerto de Registro'),
        required=True,
        copy=False,
        tracking=True)

    # Nombre
    name = fields.Char(
        string=_('Nombre'),
        required=True,
        index=True,
        copy=False,
        tracking=True)

    senial_llamada = fields.Char(
        string=_('Señal de Llamada'),
        required=False,
        index=False,
        copy=False,
        tracking=True)

    mmsi = fields.Char(
        string=_('MMSI'),
        required=False,
        index=False,
        copy=False,
        tracking=True)

    nave_zona_id = fields.Many2one(
        'nave.nave.zona',
        string=_('Última Zona Marítima'),
        tracking=True)

    nave_zona_ids = fields.Many2many(
        'nave.nave.zona',
        'nave_zona_rel',
        'nave_id',
        'zona_id',
        string=_('Zonas Marítimas habilitadas'),
        ondelete='restrict')

    nave_tipo_propulsion_id = fields.Many2one(
        'nave.tipo.propulsion',
        string=_('Tipo de Propulsion'),
        tracking=True)

    # Tipo Nave
    nave_tipo_id = fields.Many2one(
        'nave.nave.tipo',
        ondelete='restrict',
        string=_('Tipo de Nave'),
        required=True,
        copy=False,
        tracking=True)

    nave_tipo_grupo_id = fields.Many2one(
        related='nave_tipo_id.grupo_nave_id',
        string=_('Grupo del Tipo de Nave'),
        store=True,
        tracking=True)

    # Servicio
    nave_servicio_id = fields.Many2one(
        'nave.nave.servicio',
        ondelete='restrict',
        string=_('Servicio'),
        required=True,
        copy=False,
        tracking=True)

    # Origen
    nave_origen_id = fields.Many2one(
        'nave.nave.origen',
        ondelete='restrict',
        string=_('Origen'),
        required=True,
        copy=False,
        tracking=True)

    # Trafico
    tipo_trafico_id = fields.Many2one(
        'tipo.trafico',
        ondelete='restrict',
        string=_('Tipo Tráfico'),
        required=True,
        copy=False,
        tracking=True)
    
    tipo = fields.Selection(
        related='tipo_trafico_id.tipo', 
        string=_('Tipo'), 
        readonly=True, 
        store=True, 
        tracking=True)

    # Uso
    uso = fields.Selection(
        [
            ('pub', _('Publico')),
            ('com', _('Comercial')),
            ('pri', _('Privado'))
        ],
        string=_('Uso'),
        required=True,
        index=True,
        copy=False,
        tracking=True,
        default='com')

    # Material de Casco
    material_casco_id = fields.Many2one(
        'nave.casco.material',
        string='Material de Casco')

    # Avaluo
    avaluo = fields.Float(
        string=_('Avalúo'),
        required=False,
        copy=False,
        tracking=True
    )


    eslora = fields.Float(
        string=_('Eslora (mts)')
    )

    eslora_convenio = fields.Float(
        string=_('Eslora de Convenio (mts)')
    )

    eslora_pp = fields.Float(
        string=_('Eslora PP (mts)')
    )

    manga = fields.Float(
        string=_('Manga (mts)')
    )

    puntal = fields.Float(
        string=_('Puntal (mts)')
    )

    calado = fields.Float(
        string=_('Calado (mts)')
    )

    calado_aereo = fields.Float(
        string=_('Calado Aéreo (mts)')
    )

    desplazamiento = fields.Float(
        string=_('Desplazamiento (t)')
    )

    peso_muerto = fields.Float(
        string=_('Peso Muerto (t)')
    )

    # TRB
    trb = fields.Float(
        string=_('TRB'),
        required=False,
        copy=False,
        tracking=True
    )

    # TRB
    trn = fields.Float(
        string=_('TRN'),
        required=False,
        copy=False,
        tracking=True
    )

    pasajeros = fields.Float('Cap. Pasajeros')

    tripulantes = fields.Float('Cap. Tripulantes')

    # Actualizado por
    #   updated_by
    #   from 'sigmap.updated.by'

    # Lista Autorizada (habilitado para zarpe)
    lista_autorizada = fields.Selection(
        [
            ('0', 'Si'),
            ('1', 'No cumple'),
            ('2', 'Error')
        ],
        string='Cumple lista Autorizada?',
        default='1',
        required=True,
        index=True,
        copy=False,
        tracking=True)

    dms = fields.Selection(
        [
            ('sin', _('NO TIENE')),
            ('ope', _('OPERATIVO')),
            ('rep', _('OPERATIVO Y REPORTANDO'))
        ],
        string='Dispositivo DMS',
        default='sin',
        required=True,
        index=True,
        copy=False,
        tracking=True)

    active = fields.Boolean(
        string=_("Active?"),
        default=True,
        tracking=True)

    # Clave Matricula
    nave_clase_matricula_id = fields.Many2one(
        'nave.nave.clase.matricula',
        ondelete='restrict',
        string=_('Clase Matrícula'),
        required=True,
        copy=False,
        tracking=True)

    nave_estado_id = fields.Many2one('nave.nave.estado', string='Estado Operacional')

    

    aplica_descuento = fields.Boolean('Aplica descuento?')

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            rec_id = rec.id
            matricula = rec.matricula if rec.matricula not in [None, False, ''] else False
            full_name = f'[{matricula}] {name}' if matricula else f'[{rec_id}] {name}'
            result.append((rec_id, (full_name)))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            field_to_look = 'matricula' if '-' in name else 'name'
            args = [(field_to_look, operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    @api.onchange('dms')
    def _onchange_dms(self):
        if self.dms == 'rep':
            self.write({'lista_autorizada': '0'})

    # quitar _
    def _ready_for_departure_flow(self):
        self.ensure_one()
        response = dict(
            status_ok=False,
            error_message=_('Something went wrong!'),
            notifications=[])

        if self.lista_autorizada == '0':
            return dict(
                status_ok=True,
                error_message=_(''),
                notifications=[])
        if self.lista_autorizada == '1':
            notifications=[
                    'No cumple Combustible',
                    'No cumple Dotacion Minima'
            ]

            if self.dms == 'sin':
                notifications.append('No tiene dispositivo DMS operativo')

            if self.dms == 'ope':
                notifications.append('El dispositivo DMS no está reportando')

            return dict(
                status_ok=False,
                error_message=_(''),
                notifications=notifications)
        else:
            return response

    def en_fletamento_o_contrato(self):
        self.ensure_one()

        fletamentos_o_contratos_ext_ids = [
            "nave.nave_origen_flet",
            "nave.nave_origen_flet_casc",
            "nave.nave_origen_flet_expo",
            "nave.nave_origen_contr_aso",
            "nave.nave_origen_int_temp"
        ]
        fletamentos_o_contratos_ids = []
        for ext_id in fletamentos_o_contratos_ext_ids:
            try:
                origen = self.env.ref(ext_id)
                if origen.active:
                    fletamentos_o_contratos_ids.append(origen.id)
            except Exception as err:
                _logger.exception(f"External Id {ext_id} inactivo o eliminado para el modelo nave.nave.origen")

        origen = self.nave_origen_id
        return origen and origen.id in fletamentos_o_contratos_ids
