from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class DispositivoClase(models.Model):
    _name = 'nave.dispositivo.modelo.tipo.clase'

    name = fields.Char(_('Nombre'), required=True)

    codigo = fields.Char(_('Código'))

    active = fields.Boolean(_('Activo?'), default=True)


class DispositivoTipo(models.Model):
    _name = 'nave.dispositivo.modelo.tipo'

    name = fields.Char(_('Nombre'), required=True)

    codigo = fields.Char(_('Código'))

    active = fields.Boolean(_('Activo?'), default=True)

    clase_id = fields.Many2one(
        'nave.dispositivo.modelo.tipo.clase',
        string=_('Clase'),
        required=True)
    
    descripcion = fields.Char(_('Descripción'))


class DispositivoMarca(models.Model):
    _name = 'nave.dispositivo.modelo.marca'

    name = fields.Char(_('Nombre corto'), required=True)

    full_name = fields.Char(_('Nombre completo'))

    codigo = fields.Char(_('Código'))

    active = fields.Boolean(_('Activo?'), default=True)


class DispositivoModelo(models.Model):
    _name = 'nave.dispositivo.modelo'

    name = fields.Char(_('Nombre corto'), required=True)

    full_name = fields.Char(_('Nombre completo'))

    codigo = fields.Char(_('Código'))

    active = fields.Boolean(_('Activo?'), default=True)

    marca_id = fields.Many2one(
        'nave.dispositivo.modelo.marca',
        string=_('Marca'),
        required=True)
    
    tipo_id = fields.Many2one(
        'nave.dispositivo.modelo.tipo',
        string=_('Tipo'),
        required=True)

    clase_id = fields.Many2one(
        related='tipo_id.clase_id',
        string=_('Clase'),
        readonly=True)


class Dispositivo(models.Model):
    _name = 'nave.dispositivo'
    _description = _('Ship Electronic')

    numero_serie = fields.Char(string=_('Número Serial'), required=True)

    codigo = fields.Char(string=_('Código'))

    name = fields.Char(string=_('Nombre'), required=True)

    modelo_id = fields.Many2one(
        'nave.dispositivo.modelo',
        string=_('Modelo'),
        required=True)

    marca_id = fields.Many2one(
        related='modelo_id.marca_id',
        string=_('Marca'))

    tipo_id = fields.Many2one(
        related='modelo_id.tipo_id',
        string=_('Tipo'))

    clase_id = fields.Many2one(
        related='modelo_id.tipo_id.clase_id',
        string=_('Clase'))

    active = fields.Boolean(_('Activo?'), default=True)

    es_ais = fields.Boolean(_('es AIS?'), default=False)


class NaveNaveDispositivo(models.Model):
    _name = 'nave.nave.dispositivo'

    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Nave'),
        required=True)

    dispositivo_id = fields.Many2one(
        'nave.dispositivo',
        string=_('Dispositivo'),
        required=False)

    numero_serie = fields.Char(
        string='Número de Serie',
        related='dispositivo_id.numero_serie'
    )

    modelo_name = fields.Char(
        string='Modelo',
        related='dispositivo_id.modelo_id.name'
    )

    marca_name = fields.Char(
        string='Marca',
        related='dispositivo_id.modelo_id.marca_id.name'
    )

    active = fields.Boolean(
        string=_('Activo?'),
        default=True)

    fecha_inicio = fields.Date(
        string=_('Fecha Inicio'),
        required=True,
        copy=False,
        tracking=True)

    fecha_fin = fields.Date(
        string=_('Fecha Fin'),
        required=False,
        copy=False,
        tracking=True)

    licencia = fields.Char(
        string=_('Trámite'),
        required=True)

    dispositivo_valido = fields.Boolean(
        compute='_compute_dispositivo_valido',
        string=_('Habilitado?'))
    
    es_ais = fields.Boolean(
        related='dispositivo_id.es_ais',
        string=_('es AIS?'))


    @api.depends('active','licencia','fecha_inicio','fecha_fin')
    def _compute_dispositivo_valido(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.dispositivo_valido = rec.active and rec.licencia and rec.fecha_inicio and \
                                     (not rec.fecha_fin or rec.fecha_fin > today)

    def _check_dispositivo_asignado(self, vals=None, create=False):
        dispositivo_id = vals['dispositivo_id'] if 'dispositivo_id' in vals else self.dispositivo_id.id

        domain_to_look = [('dispositivo_id','=',dispositivo_id),('active','=', True)]
        if not create:
            current_id = self.id if type(self.id) == int else self.id.origin
            domain_to_look.append(('id','!=',current_id))

        dispositivos = self.env['nave.nave.dispositivo'].search(domain_to_look)
        if len(dispositivos) > 0:
            raise ValidationError(_('Ship Electronic is assigned. Search filtering by serial_number and close that assignation first!'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_dispositivo_asignado(vals=vals,create=True)
        return super().create(vals_list)

    def write(self, vals):
        self._check_dispositivo_asignado(vals=vals,create=False)
        return super().write(vals)


class Nave(models.Model):
    _inherit = 'nave.nave'

    dispositivo_ids = fields.One2many(
        'nave.nave.dispositivo',
        'nave_id',
        string=_('Electronics'))


    requiere_ais = fields.Boolean(compute='_compute_requiere_AIS', string=_('requiere AIS?')) 

    def _get_reparto_requiere_ais_ids(self):
        with_user = self.env['ir.config_parameter'].sudo()
        repartos_ids = with_user.get_param("nave.reparto_requiere_ais_ids")  # []',  '[1]', '[1, 2]'
        return literal_eval(repartos_ids) if repartos_ids else []
    
    @api.depends('reparto_id')
    def _compute_requiere_AIS(self):
        for rec in self:
            rec.requiere_ais = False
            repartos_requieren_ais_ids = self._get_reparto_requiere_ais_ids() # [],  [1], [1, 2]
            if self.env['nave.nave'].search([('id','=',rec.id),('reparto_id','child_of',repartos_requieren_ais_ids)]):
                rec.requiere_ais = True


    tiene_ais = fields.Boolean(compute='_compute_tiene_AIS', string=_('tiene AIS?'))

    @api.depends('dispositivo_ids')
    def _compute_tiene_AIS(self):
        for rec in self:
            rec.tiene_ais = False
            current_devices = [registered.dispositivo_id for registered in rec.dispositivo_ids if registered.dispositivo_valido]
            AIS_devices = [device for device in current_devices if device.es_ais]
            rec.tiene_ais = len(AIS_devices) > 0
