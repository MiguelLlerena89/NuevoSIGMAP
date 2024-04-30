from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class NaveRegla(models.AbstractModel):
    _name = "nave.domain.regla"
    _description = "Regla Base - Características de nave"
    _or_values_field = None

    OPERADORES = {
        'igual': '=',
        'no_igual': '!=',
        'mayor': '>',
        'menor': '<',
        'mayor_igual': '>=',
        'menor_igual': '<=',
        'alguno_de': 'in',
        'ninguno_de': 'not in',
        }
    # USO: operador = self.OPERADORES[self.tipo]
    # Domain: [(variable, operador, valor)]

    MODELOS = {
        "nave_tipo_grupo_id": "nave.nave.grupo",
        "nave_tipo_id": "nave.nave.tipo",
        "nave_origen_id": "nave.nave.origen",
        "bandera_pais_id": "res.country",
        "nave_servicio_id": "nave.nave.servicio",
        "nave_zona_ids": "nave.nave.zona",
        "tipo_trafico_id": "tipo.trafico",
        "nave_estado_id": "nave.nave.estado",
    }

    def _get_or_values_field(self):
        or_values_field = getattr(self, self._or_values_field)
        #if not or_values_field:
        #    raise ValidationError(f"property _or_values_field not defined in {self._name} for nave.domain.regla abstract model implementation")
        return or_values_field

    @api.model
    def selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([
            ("model", "in", ["nave.nave.grupo", "nave.nave.tipo", "nave.nave.origen", "res.country", "nave.nave.zona", "nave.nave.servicio", "tipo.trafico", "nave.nave.estado"])
        ])]

    tipo = fields.Selection([
            ("igual","Igual a"),
            ("no_igual","No igual a"),
            ("mayor","Mayor a"),
            ("menor","Menor a"),
            ("mayor_igual","Mayor o igual a"),
            ("menor_igual","Menor o igual a"),
            ("alguno_de","Alguno entre los siguientes"),
            ("ninguno_de","Ninguno de los siguientes"),
        ], string=_("Tipo de regla"), default="igual", tracking=True)
    variable = fields.Selection([
            ("eslora","Eslora"),
            ("trb","TRB"),
            ("hp","HP Máquinas Principales"),
            ("nave_tipo_grupo_id","Super Tipo nave"),
            ("nave_tipo_id","Tipo nave"),
            ("nave_origen_id","Origen"),
            ("bandera_pais_id","País de Bandera"),
            ("nave_servicio_id","Servicio nave"),
            ("nave_zona_ids","Zona Marítima"),
            ("tipo_trafico_id", "Tipo Tráfico"),
            ("nave_estado_id", "Estado Nave"),
            #("arm","Armador"),
        ], string=_("Variable"), tracking=True)
    # model_id = fields.Many2one("ir.model")
    resource_ref = fields.Reference(string='Registro', selection='selection_target_model')
    # resource_ref = '%s,%s' % (self.resource_ref._name, self.resource_ref.id)
    valor = fields.Char(string=_("Valor"), size=100, tracking=True)

    valor_str = fields.Char(string=_("Valor(es)"), compute="compute_valor_str")

    def _compute_valor_str(self):
        self.ensure_one()
        rec_valor = _("No definido")
        if self._get_or_values_field():
            rec_valor = ", ".join([reference.resource_ref.name for reference in self._get_or_values_field()])
        elif self.resource_ref:
            rec_valor = self.resource_ref.name
        else:
            rec_valor = self.valor
        return rec_valor

    @api.depends("valor", "resource_ref")
    def compute_valor_str(self):
        for rec in self:
            rec.valor_str = rec._compute_valor_str()

    """
    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.rubro_tarifa_id and rec.rubro_id:
                name = '%s: %s %s' % (rec.rubro_tarifa_id.tarifario_id.name, rec.rubro_id.name, rec.variable)
            result.append((rec.id, name))
        return result
    """

    def get_domain_tuple(self):
        self.ensure_one()
        if self._get_or_values_field():
            valor = tuple([reference.resource_ref.id for reference in self._get_or_values_field()])
        else:
            valor = self.resource_ref.id if self.resource_ref else self._compute_valor_str()

        return (self.variable, self.OPERADORES[self.tipo], valor)

class NaveReglaOpcionesOr(models.AbstractModel):
    _name = "nave.domain.regla.or"
    _description = "Regla Base - Características de nave - varias Opciones"
    _rule_parent_field = None

    def _get_rule_parent_field(self):
        rule_parent_field = getattr(self, self._rule_parent_field)
        #if not rule_parent_field:
        #    raise ValidationError(f"property _rule_parent_field not defined in {self._name} for nave.domain.regla.or abstract model implementation")
        return rule_parent_field

    def _selection_target_model(self):
        return self._get_rule_parent_field().selection_target_model()



    resource_ref = fields.Reference(string='Record', selection='_selection_target_model')
    # no need for the following (not yet)
    #  - model_id = fields.Many2one("ir.model")
    #  - valor = fields.Char(string=_("Valor"), size=100, tracking=True)
