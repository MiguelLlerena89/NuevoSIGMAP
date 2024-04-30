from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class ListaChequeo(models.Model):
    _inherit = 'nave.inspeccion'


    def _validate_antes_de_completar(self):
        self.ensure_one()
        if not self.lista_para_llenar:
            raise ValidationError('Asegurese de tener lista de chequeo e inspector correctamente asignados.')

    def _action_button_completar(self, action_id, empezar=None):
        self._validate_antes_de_completar()

        action = self.env['ir.actions.actions']._for_xml_id(action_id)
        action.update({
            'context': {
                'default_empezar': empezar or False,
                'default_inspeccion_id': self.id,
            }
        })
        return action

    def button_empezar_inspeccion(self):
        return self._action_button_completar(action_id='nave_documento.action_inspeccion_start_wizard', empezar=True)
    
    def button_completar(self):
        return self._action_button_completar(action_id='nave_documento.action_inspeccion_fill_wizard', empezar=False)

    def button_limpiar(self):
        self._validate_antes_de_completar()
        action = self.env['ir.actions.actions']._for_xml_id('nave_documento.action_inspeccion_reset_wizard')
        action.update({
            'context': {
                'default_inspeccion_id': self.id,
            }
        })
        return action

class EmpezarInspeccion(models.TransientModel):
    _name = 'nave.inspeccion.start.wizard'
    _description = _("Empezar/Completar Inspección")

    empezar = fields.Boolean(_('empezar'), default=False)

    inspeccion_id = fields.Many2one('nave.inspeccion', string=_('Inspección'))
    llenar = fields.Boolean(_('Pre - llenado?'), default=False)

    respuesta = fields.Selection(
        string=_("Respuesta"),
        selection=[
            ('sat', _("Satisfactorio")),
            ('obs', _("Observación")),
            ('nos', _("No Satisfactorio")),
        ],
        default=False)

    def _button_llenar_preguntas(self, cambiar_estado=None):
        self.ensure_one()
        inspeccion = self.inspeccion_id
    
        if self.empezar and cambiar_estado:
            inspeccion.estado_lista_chequeo = 'llenando'

        if self.llenar and self.respuesta and inspeccion.lista_chequeo_pregunta_ids:
            for pregunta in inspeccion.lista_chequeo_pregunta_ids:
                if not pregunta.display_type and not pregunta.has_child_ids and not pregunta.respuesta:
                    pregunta.respuesta = self.respuesta

    def button_empezar_a_llenar(self):
        self._button_llenar_preguntas(cambiar_estado=True)

    def button_completar_preguntas(self):
        self._button_llenar_preguntas(cambiar_estado=False)

class LimpiarInspeccion(models.TransientModel):
    _name = 'nave.inspeccion.reset.wizard'
    _description = _("Limpiear/Resetear Inspección")

    inspeccion_id = fields.Many2one('nave.inspeccion', string=_('Inspección'))
    limpiar = fields.Boolean(_('Confirmar'), default=False)

    def button_limpiar(self):
        self.ensure_one()
        inspeccion = self.inspeccion_id
        if self.limpiar and inspeccion.lista_chequeo_pregunta_ids:
            inspeccion.estado_lista_chequeo = 'por_llenar'
            for pregunta in inspeccion.lista_chequeo_pregunta_ids:
                pregunta.limpiar_pregunta()
