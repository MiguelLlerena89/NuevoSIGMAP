from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class Tramite(models.Model):
    _inherit = 'tramite'

    # Inspección

    nave_trb = fields.Float(
        related='order_id.nave_id.trb',
        string=_('TRB'),
        store=True,
        copy=False,
        readonly=True)
    nave_origen_id = fields.Many2one(
        related='order_id.nave_id.nave_origen_id',
        string=_("Orígen"),
        store=True,
        copy=False,
        readonly=True)
    tipo_inspector_id = fields.Many2one(
        comodel_name='sigmap.inspector.tipo',
        string=_('Tipo Inspector'),
        index=True,
        copy=False,
        tracking=True)

    lista_chequeo_id = fields.Many2one("lista.chequeo", "Lista chequeo", index=True, copy=False, tracking=True)
    lista_chequeo_error_msg = fields.Text(string=_('Lista Chequeo (Error Asignación)'), index=True, copy=False, tracking=True)

    puerto_id = fields.Many2one("sigmap.puerto", "Puerto", tracking=True)
    lugar_inspeccion = fields.Char(string=_('Lugar de inspección'), tracking=True)
    lugar_embarque = fields.Char(string=_('Lugar de embarque'), tracking=True)
    contacto = fields.Char(string=_('Contacto'), tracking=True)
    telefono = fields.Char(string=_('Teléfono de contacto'), tracking=True)

    nave_inspeccion_id = fields.Many2one("nave.inspeccion", string=_("Inspección"), index=True, copy=False, tracking=True)
    nave_inspeccion_state = fields.Selection(
        related="nave_inspeccion_id.state",
        string=_("Estado Inspección"),
        readonly=True)
    nave_inspeccion_resultado = fields.Selection(
        related="nave_inspeccion_id.estado_lista_chequeo",
        string=_("Estado lista chequeo"),
        readonly=True)

    # Permiso Vare/Desvare
    varadero_id = fields.Many2one('nave.empresa.mantenimiento', string='Varadero', index=True, copy=False, tracking=True)
    varadero_matricula_caducidad = fields.Char(
        related='varadero_id.matricula_caducidad',
        string=_('Licencia caduca'),
        readonly=True)
    varadero_matricula_estado = fields.Char(
        related='varadero_id.matricula_estado',
        string=_('Licencia?'),
        readonly=True)
    fecha_vare = fields.Date('Fecha de Vare', index=True, copy=False, tracking=True) #default=fields.Datetime.today
    fecha_desvare = fields.Date('Fecha de DesVare', index=True, copy=False, tracking=True) #default=fields.Datetime.today


    @api.onchange('servicio_id', 'es_inspeccion')
    def _onchange_servicio_id_para_lista_chequeo(self):
        if self.servicio_id and self.servicio_id.es_inspeccion:
            self.lista_chequeo_id, self.lista_chequeo_error_msg = self.nave_id.find_listas_chequeo_for_service(self.servicio_id.id)
            if not self.lista_chequeo_id and not self.env['lista.chequeo'].search([('servicio_id.id','=',self.servicio_id.id)]):
                self.lista_chequeo_error_msg = f"No hay listas de chequeo configuradas para esta inspección: {self.servicio_id.name}"

            self.tipo_inspector_id = self.nave_id.get_tipo_de_inspector()


    def action_iniciar_tramite(self):
        if self.completado and self.es_inspeccion:
            if not self.lista_chequeo_id:
                raise ValidationError(_(f'No se puede iniciar el trámite!\n{self.lista_chequeo_error_msg}'))

            inspeccion = self.env['nave.inspeccion'].create({
                'tramite_id': self.id,
                'puerto_id': self.puerto_id.id,
                'lugar_inspeccion': self.lugar_inspeccion,
                'lugar_embarque': self.lugar_embarque,
                'contacto': self.contacto,
                'telefono': self.telefono,
                'lista_chequeo_id': self.lista_chequeo_id.id,
                'state': 'por_asignar_inspector',
                'estado_lista_chequeo': 'por_llenar',
            })

            if inspeccion:
                self.nave_inspeccion_id = inspeccion

        super().action_iniciar_tramite()

        if self.nave_id and self.servicio_id.es_texto_html and self.servicio_id.plantilla_texto:
            if self.servicio_id.model_model in ['nave.documento.certificado']:
                self.resource_ref.descripcion = self.nave_id.llenar_plantilla(self.servicio_id.plantilla_texto)
