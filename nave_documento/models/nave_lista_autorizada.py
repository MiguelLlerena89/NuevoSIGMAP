from odoo import api, fields, models, _

class NaveListaAutorizada(models.Model):
    _name = 'nave.lista.autorizada'
    _description = _('Lista autorizada de naves')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Nombre
    name = fields.Char(
        string=_('Name'),
        required=True,
        index=True,
        copy=False,
        tracking=True)
    #
    check_min = fields.Boolean(string=_("Mínimo?"), default=True, tracking=True)
    min_trb = fields.Integer(string=_("Mínimo"), default=0, tracking=True)
    check_max = fields.Boolean(string=_("Máximo?"), default=True, tracking=True)
    max_trb = fields.Integer(string=_("Máximo"), default=0, tracking=True)
    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)

    servicio_nave_id = fields.Many2one("nave.nave.servicio", "Tipo servicio", tracking=True)
    #

    documento_ids = fields.One2many("nave.lista.autorizada.linea", "lista_autorizada_id", "Servicios", tracking=True)
    regla_ids = fields.One2many("nave.lista.autorizada.regla", "lista_autorizada_id", "Reglas", tracking=True)


class NaveListaAutorizadaLinea(models.Model):
    _name = 'nave.lista.autorizada.linea'
    _description = _('Línea lista autorizada de naves')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    servicio_id = fields.Many2one("tramite.documento", "Servicios", tracking=True)
    lista_autorizada_id = fields.Many2one("nave.lista.autorizada", "Lista autorizada")


class NaveListaAutorizadaRegla(models.Model):
    _name = 'nave.lista.autorizada.regla'
    _description = _('Regla - lista autorizada de naves')
    _inherit = ['nave.domain.regla', 'mail.thread', 'mail.activity.mixin']
    _or_values_field = "regla_or_ids"

    lista_autorizada_id = fields.Many2one("nave.lista.autorizada", "Lista autorizada")
    regla_or_ids = fields.One2many("nave.lista.autorizada.regla.or", "lista_autorizada_regla_id", "Opciones", tracking=True)


class NaveListaAutorizadaReglaOr(models.Model):
    _name = 'nave.lista.autorizada.regla.or'
    _description = _('Regla Opciones - lista autorizada de naves')
    _inherit = ['nave.domain.regla.or', 'mail.thread', 'mail.activity.mixin']
    _rule_parent_field = "lista_autorizada_regla_id"

    lista_autorizada_regla_id = fields.Many2one("nave.lista.autorizada.regla", "Lista autorizada - Regla")
    regla_variable = fields.Selection(
        related="lista_autorizada_regla_id.variable", string=_("Variable"), tracking=True)
