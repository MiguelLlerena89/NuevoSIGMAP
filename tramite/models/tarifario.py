from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class TramiteTarifario(models.Model):
    _name = "tramite.tarifario"
    _description = "Trámite tarifario"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Institución"),
        default=_default_company,
        tracking=True
    )
    name = fields.Char(string=_("Nombre"), size=100, tracking=True)
    year = fields.Char(string=_("Año"), size=4, index=True, tracking=True)
    rubro_ids = fields.One2many("product.template", "tarifario_id", string=_("Rubro"), tracking=True)
    detalle = fields.Char(string=_("Nombre oficial"), size=100, tracking=True)
    registro_oficial = fields.Char(string=_("Órden general registro oficial"), size=100, tracking=True)
    active = fields.Boolean(string=_("Activo?"), default=True,tracking=True)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Rubro"
    _order = "name"

    tarifario_id = fields.Many2one("tramite.tarifario", string=_("Tarifario"), index=True, tracking=True)
    valor = fields.Char(string=_("Valor"), size=100, tracking=True)
    active = fields.Boolean(string=_("Activo?"))
    tiene_interes = fields.Boolean(
        string=_("Interés por mora?"), default=False, index=True, tracking=True)
    articulo = fields.Char(string=_("Artículo"), size=10, tracking=True)
    literal = fields.Char(string=_("Literal"), size=10, tracking=True)
    numeral = fields.Char(string=_("Numeral"), size=10, tracking=True)
    servicio_id = fields.Many2one("tramite.documento", string=_("Documento"), tracking=True)
    tipo_documento_id = fields.Many2one(related="servicio_id.tipo_documento_id", string=_("Tipo Documento"), tracking=True, store=True)
    list_price = fields.Float(compute="_compute_amount", store=True, readonly=False)
    #rubro_maestro: para ser usado cuando el rubro requiera ej. sacar un porcentaje de un rubro mayor.
    rubro_maestro_id = fields.Many2one("product.template", string=_("Rubro maestro"), index=True, tracking=True)
    porcentaje_maestro = fields.Integer(string=_("Porcentaje maestro"), default=0, tracking=True)
    incremento_anual = fields.Boolean(string=_("Aplica incremento anual?"), default=True, tracking=True)
    orden = fields.Integer(string=_("Órden"), default=1, tracking=True)
    tarifa_ids = fields.One2many("rubro.tarifa", "rubro_id", "Tarifas rubross", tracking=True)

    es_inspeccion = fields.Boolean(related="servicio_id.es_inspeccion", string=_('Es inspección?'), tracking=True)
    tipo_inspeccion = fields.Selection(
        [
            ('ini', 'Inicial o Renovación'),
            ('rei', 'Reinspección'),
            ('end', 'Endoso'),
            ('ext', 'Extensión'),
        ],
        string=_('Tipo Inspección'), default=False, tracking=True)

    porcentaje_recargo_nave_int = fields.Integer(string=_("Porcentaje Recargo Naves Extranjeras"), tracking=True)
    monto_max_nave_int = fields.Float(string=_("Monto Máximo Naves Extranjeras"), tracking=True)

    @api.onchange('rubro_maestro_id')
    def _onchange_beneficiario_id(self):
        if not self.rubro_maestro_id:
            self.porcentaje_maestro = 0
        else:
            self.incremento_anual = False

class RubroTarifa(models.Model):
    _name = "rubro.tarifa"
    _description = "Tarifas de rubro"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string=_("Nombre"), size=100, tracking=True)
    rubro_id = fields.Many2one("product.template", string=_("Rubro"), index=True, tracking=True)
    tarifario_id = fields.Many2one(related='rubro_id.tarifario_id', string=_("Tarifario"), index=True, tracking=True)
    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)
    tipo = fields.Selection([
            ("constante","Constante"),
            ("formula","Fórmula"),
            ("porcentaje","Porcentaje"),
        ], string=_("Tipo de rubro"), default="constante", tracking=True)
    variable = fields.Selection([
            ("trb","TRB"),
            ("eslora","Eslora"),
            ("motor","Motor"),
            ("sbu","SBU"),
            #("zona_maritima_autorizada","Zona marítima autorizada"),
        ], string=_("Variable"),  tracking=True)
    operador = fields.Selection([
            ("or","OR"),
            ("and","AND"),
        ], string=_("Tipo de operador"), tracking=True)
    literal = fields.Char(string=_("Literal"), size=10, tracking=True)
    valor_minimo = fields.Float(string=_("Valor mínimo"), tracking=True)
    valor_maximo = fields.Float(string=_("Valor máximo"), tracking=True)
    monto = fields.Float(string="Monto")
    monto_base = fields.Float(string="Monto base")
    fecha_inicio = fields.Date(
        string="Fecha inicio",
        tracking=True,
    )
    fecha_fin = fields.Date(
        string="Fecha caducidad",
        tracking=True,
    )
    #si el tarifario tiene más de un registro y no tiene regla salta mensaje porque no se podría saber cuál elegir, si tiene 1 registro puedo usar ese tarifario
    regla_ids = fields.One2many("rubro.regla", "rubro_tarifa_id", "Reglas", tracking="1")
    valor_ids = fields.One2many("rubro.tarifa.valor", "rubro_tarifa_id", "Valores", tracking="1")

    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.tarifario_id and rec.rubro_id:
                name = '%s: %s' % (rec.tarifario_id.name, rec.rubro_id.name)
            result.append((rec.id, name))
        return result

    def get_monto_tarifa(self):
        today = fields.Date.context_today(self).strftime('%Y-%m-%d %H:%M:%S')

        valor_tarifa = self.env['rubro.tarifa.valor'].search(
            [
                ('rubro_tarifa_id', '=', self.id),
                ('active', '=', True),
                ('fecha_desde', '>=', today),
                ('fecha_hasta', '<=', today)
            ]
        )
        if valor_tarifa:
            monto = valor_tarifa.monto
            minimo = valor_tarifa.valor_minimo
            maximo = valor_tarifa.valor_maximo
        else:
            monto = self.monto
            minimo = self.valor_minimo
            maximo = self.valor_maximo

        return monto, minimo, maximo


#valores_tarifarios todos los registros anuales del tarifario que cambia anualmente aquí se aplica el índice de inflación
class RubroTarifaValor(models.Model):
    _name = "rubro.tarifa.valor"
    _description = "Valores por tarifa de rubros"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    rubro_tarifa_id = fields.Many2one("rubro.tarifa", string=_("Tarifa"), index=True, tracking=True)
    rubro_id = fields.Many2one(related="rubro_tarifa_id.rubro_id", string=_("Rubro"), index=True, tracking=True)
    incremento = fields.Float(string="Incremento")
    valor_anterior = fields.Float(string="Monto anterior")
    monto = fields.Float(string="Monto")
    valor_minimo = fields.Char(string="Monto mínimo")
    valor_maximo = fields.Char(string="Monto máximo")
    year = fields.Integer("Año", required=True)

    fecha_desde = fields.Datetime(
        string="Fecha desde",
        tracking=True,
    )
    fecha_hasta = fields.Datetime(
        string="Fecha hasta",
        tracking=True,
    )
    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)


class RubroRegla(models.Model):
    _name = "rubro.regla"
    _description = "Reglas de rubro"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    OPERADORES = {
         'igual': '=',
         'no_igual': '!=',
         'mayor': '>',
         'menor': '<',
         'mayor_igual': '>=',
         'menor_igual': '>=',
         }
    # USO: operador = self.OPERADORES[self.tipo]
    # Domain: [(variable, operador, valor)]

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([
            ("model", "in", [
                "personal.maritimo.catalogo.jerarquia",
                "permar.permiso.provisional.embarque.tipo",
                "nave.nave.grupo",
                "nave.nave.tipo",
                "nave.nave.origen",
                "nave.nave.zona",
                "nave.nave.servicio",
                "tipo.trafico",
                "nave.nave.estado"
                ])
            #("model", "in", ["personal.maritimo.catalogo.jerarquia", "nave.nave.tipo", "res.country"])
        ])]

    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)
    rubro_tarifa_id = fields.Many2one("rubro.tarifa", string=_("Tarifa"), index=True, tracking=True)
    rubro_id = fields.Many2one(related="rubro_tarifa_id.rubro_id", string=_("Rubro"), index=True, tracking=True)
    tipo = fields.Selection([
            ("igual","Igual a"),
            ("no_igual","No igual a"),
            ("mayor","Mayor a"),
            ("menor","Menor a"),
            ("mayor_igual","Mayor o igual a"),
            ("menor_igual","Menor o igual a"),
        ], string=_("Tipo de regla"), default="igual", tracking=True)
    variable = fields.Selection([
            ("eslora","Eslora"),
            ("trb","TRB"),
            ("jerarquia","Jerarquía"),
            ("tipo_permiso_id", "Tipo permiso"),
            ("nave_tipo_grupo_id","Super Tipo nave"),
            ("nave_tipo_id","Tipo nave"),
            ("nave_origen_id","Origen"),
            #("nacionalidad","Nacionalidad"),
            ("nave_servicio_id","Servicio nave"),
            ("nave_zona_ids","Zona Marítima"),
            ("tipo_trafico_id", "Tipo Tráfico"),
            ("nave_estado_id", "Estado Nave"),
            #("arm","Armador"),
        ], string=_("Variable"), tracking=True)
    model_id = fields.Many2one("ir.model")
    resource_ref = fields.Reference(string='Record', selection='_selection_target_model')
    # en caso de jerarquía debería valor debería tener el id de jerarquía
    valor = fields.Char(string=_("Valor"), size=100, tracking=True)
    # resource_ref = '%s,%s' % (self.resource_ref._name, self.resource_ref.id)

    def name_get(self):
        result = []
        for rec in self:
            name = ''
            if rec.rubro_tarifa_id and rec.rubro_id:
                name = '%s: %s %s' % (rec.rubro_tarifa_id.tarifario_id.name, rec.rubro_id.name, rec.variable)
            result.append((rec.id, name))
        return result

