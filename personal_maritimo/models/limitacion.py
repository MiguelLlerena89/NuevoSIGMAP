from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError
from dateutil.relativedelta import relativedelta

import logging

_logger = logging.getLogger(__name__)


class PMCatalogoLimitacion(models.Model):
    _name = "personal.maritimo.catalogo.limitacion"
    _description = "Limitaciones"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True
    )
    name = fields.Char(string=_("Descripción"), size=100, index=True, tracking=True)
    articulo = fields.Char(string=_("Artículo"), size=100, index=True, tracking=True)
    descripcion_en = fields.Char(string=_("Descripción inglés"), size=100, index=True, tracking=True)
    observacion = fields.Char(string=_("Observación"), size=100, index=True, tracking=True)
    line_ids = fields.One2many('personal.maritimo.catalogo.curso.line', 'limitacion_id', string='Cursos')
    jerarquia_ids = fields.One2many('personal.maritimo.limitacion.jerarquia', 'limitacion_id', string='Jerarquía')
    check_jeraquias_todas = fields.Boolean('Aplica para todas las jerarquías?', default=True)
    check_jerarquias_oficiales = fields.Boolean('Aplica para oficiales?', default=True)
    check_naves_todas = fields.Boolean('Aplica para todas las naves?', default=True)
    tipo_nave_id = fields.Many2one('nave.nave.tipo', string='Tipo de nave')

class CursoLine(models.Model):
    _inherit = 'personal.maritimo.catalogo.curso.line'

    limitacion_id = fields.Many2one('personal.maritimo.catalogo.limitacion', string='Limitación')

class JerarquiaLine(models.Model):
    _name = 'personal.maritimo.limitacion.jerarquia'
    _description = 'Líneas de jerarquia'

    limitacion_id = fields.Many2one('personal.maritimo.catalogo.limitacion', string='Limitacion')
    jerarquia_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string='Jerarquia')