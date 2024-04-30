from odoo import api, fields, models, _

class NaveDotacionMinima(models.Model):
    _name = 'nave.dotacion.minima'
    _description = _('Dotación Mínima de naves')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Nombre
    name = fields.Char(
        string=_('Name'),
        required=True,
        index=True,
        copy=False,
        tracking=True)
    check_min = fields.Boolean(string=_("Mínimo?"), default=True,tracking=True)
    min_trb = fields.Integer(string=_("Mínimo"), default=0, tracking=True)
    check_max = fields.Boolean(string=_("Máximo?"), default=True,tracking=True)
    max_trb = fields.Integer(string=_("Máximo"), default=0, tracking=True)
    active = fields.Boolean(string=_("Activo?"), default=True,tracking=True)

    servicio_nave_id = fields.Many2one("nave.nave.servicio", "Tipo servicio", tracking=True)
    trafico_nave_id = fields.Many2one("tipo.trafico", "Tipo trafico", tracking=True)
    zona_nave_ids = fields.Many2many('nave.nave.zona', string='Zona Marítima', tracking=True)

    min_potencia = fields.Integer(string=_("Mínimo"), default=0, tracking=True)
    max_potencia = fields.Integer(string=_("Máximo"), default=0, tracking=True)

    jerarquia_ids = fields.One2many("nave.dotacion.minima.linea", "dotacion_minima_id", "Jerarquías", tracking=True)
    regla_ids = fields.One2many("nave.dotacion.regla", "dotacion_id", "Reglas", tracking=True)

class NaveDotacionMinimaLinea(models.Model):
    _name = 'nave.dotacion.minima.linea'
    _description = _('Línea dotacion minima de naves')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    jerarquia_id = fields.Many2one("personal.maritimo.catalogo.jerarquia", "Jerarquía", tracking=True)
    number = fields.Integer('# Tripulantes')
    dotacion_minima_id = fields.Many2one("nave.dotacion.minima", "Dotación Mínima")

class NaveListaAutorizadaRegla(models.Model):
    _name = 'nave.dotacion.regla'
    _description = _('Regla - Dotacion Mínima de naves')
    _inherit = ['nave.domain.regla', 'mail.thread', 'mail.activity.mixin']
    _or_values_field = "regla_or_ids"

    dotacion_id = fields.Many2one("nave.dotacion.minima", "Dotacion Mínima")
    regla_or_ids = fields.One2many("nave.dotacion.regla.or", "dotacion_regla_id", "Opciones", tracking=True)


class NaveListaAutorizadaReglaOr(models.Model):
    _name = 'nave.dotacion.regla.or'
    _description = _('Regla Opciones - Dotacion Mínima de naves')
    _inherit = ['nave.domain.regla.or', 'mail.thread', 'mail.activity.mixin']
    _rule_parent_field = "dotacion_regla_id"

    dotacion_regla_id = fields.Many2one("nave.dotacion.regla", "Dotacion Mínima - Regla")
    regla_variable = fields.Selection(
        related="dotacion_regla_id.variable", string=_("Variable"), tracking=True)