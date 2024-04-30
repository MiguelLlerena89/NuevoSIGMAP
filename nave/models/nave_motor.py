from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class DispositivoClase(models.Model):
    _name = 'nave.maquina.combustible.clase'

    # GAS OIL

    name = fields.Char(_('Nombre'), required=True)
    codigo = fields.Char(_('Código'))
    active = fields.Boolean(_('Activo?'), default=True)


class MaquinaCombustibleTipo(models.Model):
    _name = 'nave.maquina.combustible'

    name = fields.Char(_('Nombre'), required=True)
    clase_id = fields.Many2one('nave.maquina.combustible.clase', string=_('Clase'))
    codigo_petroecuador = fields.Char(_('Código Petroecuador'))
    active = fields.Boolean(_('Activo?'), default=True)


class MaquinaTipo(models.Model):
    _name = 'nave.maquina.modelo.tipo'

    name = fields.Char(_('Nombre'), required=True)
    descripcion = fields.Char(_('Descripción'))

    codigo = fields.Char(_('Código'))
    active = fields.Boolean(_('Activo?'), default=True)


class MaquinaMarca(models.Model):
    _name = 'nave.maquina.modelo.marca'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Nombre corto'),
        required=True)

    full_name = fields.Char(_('Nombre completo'))

    codigo_troquelado = fields.Char(
        string=_('Código - Troquelado Motor'),
        size=2,
        index=True,
        required=True,
        tracking=True)

    codigo = fields.Char(_('Código'))
    active = fields.Boolean(
        string=_('Activo?'),
        default=True)


class MaquinaModelo(models.Model):
    _name = 'nave.maquina.modelo'

    name = fields.Char(_('Nombre corto'), required=True)

    full_name = fields.Char(_('Nombre completo'))

    codigo = fields.Char(_('Código'))

    """
    numero_cilindros = fields.Integer(
        string=_('Número Cilindros'),
        index=True,
        tracking=True)

    potencia = fields.Integer(
        string=_('Potencia'),
        index=True,
        tracking=True)

    potencia_unidad = fields.Selection([
            ('hp', _('HP')),
            ('kw', _('KW')),
            ('kva', _('KVA')),
        ],
        string=_('Potencia Unidad'),
        default='hp',
        index=True,
        copy=False,
        tracking=True)

    consumo = fields.Float(
        string=_('Consumo (Gal/h)'),
        index=True,
        tracking=True)

    velocidad = fields.Integer(
        string=_('Velocidad (rpm)'),
        index=True,
        tracking=True)
    """

    active = fields.Boolean(_('Activo?'), default=True)

    marca_id = fields.Many2one(
        'nave.maquina.modelo.marca',
        string=_('Marca'),
        required=True)

    maquinaria = fields.Selection([
        ('pri', 'Principal'),
        ('aux', 'Auxiliar'),
    ], string=_('Máquina'), default='pri', index=True, copy=False, tracking=True)

    tipo_maquinaria = fields.Selection([
        ('fuera_borda', 'Fuera de Borda'),
        ('estacionario', 'Estacionario'),
    ], string=_('Tipo Máquina'), default='fuera_borda', index=True, copy=False, tracking=True)

    """
    tipo_id = fields.Many2one(
        'nave.maquina.modelo.tipo',
        string=_('Tipo'),
        required=True)

    categoria_motor = fields.Selection([
        ('motor', _('Motor')),
        ('bomba', _('Bomba')),
        ('gener', _('Generador'))
    ], string=_('Categoría'), default='motor', index=True, copy=False, tracking=True)

    tipo_combustible_id = fields.Many2one(
        'nave.maquina.combustible',
        string=_('Tipo Combustible'))
    
    clase_combustible_id = fields.Many2one(
        related='tipo_combustible_id.clase_id',
        string=_('Tipo Combustible'))
    """

class Maquina(models.Model):
    _name = 'nave.maquina'
    _description = _('Máquina')
    _inherit = ['mail.thread', 'mail.activity.mixin']


    # tipo_maquina_id
    # tipo_combustible_id
    # tipo_maquinaria PRINCIPAL AUXILIAR


    # serial    
    # codigo_motor = fields.Char(string=_('Código Motor'), index=True, tracking=True)
    # serie = fields.Char(string=_('Serie'), index=True, tracking=True)
    numero_serie = fields.Char(
        string=_('Serial'),
        index=True,
        tracking=True)

    # modelo = fields.Char(string=_('Motor Model'), index=True, tracking=True)
    modelo_id = modelo_id = fields.Many2one(
        'nave.maquina.modelo',
        string=_('Modelo'),
        required=True,
        tracking=True)

    #tipo_marca = fields.Char(string=_('Motor Brand'), index=True, tracking=True)
    marca_id = fields.Many2one(
        related='modelo_id.marca_id',
        string=_('Marca'))

    tipo_maquinaria = fields.Selection(
        related='modelo_id.tipo_maquinaria', 
        string=_('Tipo Máquina'))

    maquinaria = fields.Selection([
        ('pri', 'Principal'),
        ('aux', 'Auxiliar'),
    ], string=_('Máquina'), default='pri', index=True, copy=False, tracking=True)

    numero_cilindros = fields.Integer(
        string=_('Número Cilindros'),
        index=True,
        tracking=True)

    potencia = fields.Integer(
        string=_('Potencia'),
        index=True,
        tracking=True)

    potencia_motor = fields.Selection([
            ('hp', _('HP')),
            ('kw', _('KW')),
        ],
        string=_('Potencia Unidad'),
        default='hp',
        index=True,
        copy=False,
        tracking=True)

    consumo = fields.Float(
        string=_('Consumo (Gal/h)'),
        index=True,
        tracking=True)

    velocidad = fields.Integer(
        string=_('Velocidad (rpm)'),
        index=True,
        tracking=True)

    fecha_construccion = fields.Date(
        string=_('Fecha Fabricación'),
        required=True,
        copy=False)

    propietario = fields.Many2one(
        'nave.nave.propietario',
        string=_('Propietario'),
        index=True,
        tracking=True,
        required=True)

    clase = fields.Selection([
        ('meca', _('Mecánico')),
        ('elec', _('Eléctrico')),
        ('meca_elec', _('Mecánico - Eléctrico'))
    ], string=_('Clase'), default='meca', index=True, copy=False, tracking=True)

    tipo_combustible_id = fields.Many2one(
        'nave.maquina.combustible',
        string=_('Tipo Combustible'))
    
    clase_combustible_id = fields.Many2one(
        related='tipo_combustible_id.clase_id',
        string=_('Tipo Combustible'))

    # Para auxiliares
    numero_serie_generador = fields.Char(
        string=_('Serial Generador'),
        index=True,
        tracking=True)

    potencia_generador = fields.Integer(
        string=_('Potencia Generador (kVA)'),
        index=True,
        tracking=True)


    # Para fuera de borda
    codigo_troquelado = fields.Char(
        string=_('Código Troquelado'),
        index=True,
        tracking=True)


    active = fields.Boolean(string=_("Active?"), default=True, tracking=True)
