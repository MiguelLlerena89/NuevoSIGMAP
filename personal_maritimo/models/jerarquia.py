
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class Jerarquia(models.Model):
    _name = "personal.maritimo.catalogo.jerarquia"
    _description = "Jerarquía/Especialidad"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)

    name = fields.Char(string=_("Nombre"), size=100, index=True, tracking=True)
    resolucion = fields.Char(string=_("Resolución"), size=100, index=True, tracking=True)
    descripcion_es = fields.Char(string=_("Descripción español"), size=100, index=True, tracking=True)
    descripcion_en = fields.Char(string=_("Descripción inglés"), size=100, index=True, tracking=True)
    funcion_es = fields.Char(string=_("Función español"), size=100, index=True, tracking=True)
    funcion_en = fields.Char(string=_("Función inglés"), size=100, index=True, tracking=True)
    nivel_es = fields.Char(string=_("Nivel español"), size=100, index=True, tracking=True)
    nivel_en = fields.Char(string=_("Nivel inglés"), size=100, index=True, tracking=True)
    descripcion = fields.Char(string=_("Descripción"), size=100, index=True, tracking=True)
    abreviatura = fields.Char(string=_("Abreviatura"), size=100, index=True, tracking=True)
    capitulo = fields.Char(string=_("Capítulo"), size=5, index=True, tracking=True)
    regla = fields.Char(string=_("Regla"), size=5, index=True, tracking=True)
    seccion = fields.Char(string=_("Sección"), size=5, index=True, tracking=True)
    vigencia = fields.Integer(string='Vigencia(años)', default=2)
    tee = fields.Integer(string='Tiempo efectivo de embarque (años)', default=0)
    curso_id = fields.Many2one(
        "personal.maritimo.catalogo.curso",
        string=_("Curso formación"),
        tracking=True)
    jerarquia_id = fields.Many2one(
        "personal.maritimo.catalogo.jerarquia",
        string=_("Jerarquía padre"),
        tracking=True)
    clasificacion_id = fields.Many2one(
        "personal.maritimo.clasificacion",
        string=_("Clasficación"),
        tracking=True)
    tipo_personal = fields.Selection(
        selection=[
            ("cubierta", "Cubierta"),
            ("maquina", "Maquina"),
        ],
        string="Tipo personal",
        copy=False,
        tracking=True,
        default="cubierta",
    )
    tipo_jerarquia = fields.Selection(
        selection=[
            ("oficial", "Oficial"),
            ("tripulante", "Tripulante"),
        ],
        string="Tipo jerarquía",
        copy=False,
        tracking=True,
        default="tripulante",
    )
    requisito_ids = fields.One2many(
        "personal.maritimo.catalogo.jerarquia.curso",
        "jerarquia_id",
        string="Cursos requeridos",
        tracking=True
    )
    limitacion_id = fields.Many2one(
        "personal.maritimo.catalogo.limitacion",
        string=_("limitacion"),
        tracking=True)

    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)


class JerarquiaCurso(models.Model):
    _name = 'personal.maritimo.catalogo.jerarquia.curso'
    _description = 'Cursos requeridos jerarquia'

    curso_id = fields.Many2one('personal.maritimo.catalogo.curso', string='Curso')
    jerarquia_id = fields.Many2one('personal.maritimo.catalogo.jerarquia', string='Jerarquía')


class PersonalMaritimoClasificacion(models.Model):
    _name = "personal.maritimo.clasificacion"
    _description = "Clasificación personal marítimo"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)

    name = fields.Char(string=_("Nombre"), size=100, index=True, tracking=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)
