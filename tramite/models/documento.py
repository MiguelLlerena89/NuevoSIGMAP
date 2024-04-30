
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)


class TramiteDocumento(models.Model):
    _name = "tramite.documento"
    _description = "Documento del trámite"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = 'name'

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True
    )
    name = fields.Char(string=_("Nombre"), size=200, index=True, tracking=True)

    #categoria_id = fields.Many2one("categoria.documento", string=_("Categoría"), tracking=True)
    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)
    emitido_por_dirnea = fields.Boolean(
        string=_("¿Emitido por la Institución?"),
        default=True,
        tracking=True
    )
    validar_cursos_omi = fields.Boolean(
        string=_("Validar cursos OMI?"),
        default=True,
        tracking=True
    )
    validar_cursos_formacion = fields.Boolean(
        string=_("Validar cursos formación?"),
        default=True,
        tracking=True
    )
    validar_jerarquia = fields.Boolean(
        string=_("Validar jerarquía?"),
        default=False,
        tracking=True
    )
    requisito_ids = fields.One2many(
        "tramite.documento.requisito",
        "servicio_id",
        string="Requisitos",
        tracking=True
    )
    rubro_ids = fields.One2many("product.template", "servicio_id", string=_("Rubro"), tracking=True)
    model_id = fields.Many2one("ir.model")
    model_name = fields.Char(related="model_id.name")
    model_model = fields.Char(related="model_id.model")
    departamento_id = fields.Many2one("sigmap.departamento", string=_("Departamento"), tracking=True, store=True)
    tipo_documento_id = fields.Many2one("sigmap.documento.tipo", string=_("Tipo Documento"), tracking=True, store=True)
    es_cert_estatutario_naves = fields.Boolean('¿Es Certificado Estaturario de Nave?', default=False, copy=True, index=True, tracking=True)
    es_derecho_anual_naves = fields.Boolean('¿Es Derecho Anual?', default=False, copy=True, index=True, tracking=True)
    es_oficio = fields.Boolean('¿Es Oficio?', default=False, copy=True, index=True, tracking=True)
    es_documento_tecnico = fields.Boolean('¿Es Documento Técnico?', default=False, copy=True, index=True, tracking=True)
    es_documento_extranjero = fields.Boolean('¿Es Documento Extranjero?', default=False, copy=True, index=True, tracking=True)
    caduca = fields.Boolean('¿Caduca?', default=True, copy=True, index=True, tracking=True)
    tipo_reparto_id = fields.Many2one("sigmap.reparto.tipo", string=_("Tipo de Reparto"), tracking=True, store=True)
    reparto_ids = fields.One2many("tramite.documento.reparto", "servicio_id", string=_("Reparto"), tracking=True)
    es_provisional = fields.Boolean('¿Es Provisional?', copy=False, index=True, tracking=True)

    check_refrendo = fields.Boolean("Revisa refrendo/certificado de cursos", tracking=True)

    titulo_reporte = fields.Char('Título de encabezado de reporte (Español)')
    titulo_reporte_en = fields.Char('Título de encabezado de reporte (Inglés)')

    attachments_required = fields.Boolean(_('Required Attachments'), default=False,
                        help="If you enable this option, it will be mandatory to attach file(s) to this record")

    periodo_caducidad = fields.Selection([
        ('years', _('Años')),
        ('months', _('Meses')),
        ('days', _('Días')),
    ], string='Período de Caducidad', default='years', copy=True, tracking=True)
    caducidad = fields.Integer(string=_("Caducidad"), default=1, copy=True, tracking=True)
    caducidad_extension = fields.Integer(string=_("Caducidad Extensión (Meses)"), default=False, copy=True, tracking=True)
    caducidad_condicional = fields.Integer(string=_("Caducidad como Satisfactorio Condicional (Meses)"), default=False, copy=True, tracking=True)

    tiene_vigencia_minima = fields.Boolean('¿Tiene vigencia mínima?', default=False, copy=True, index=True, tracking=True)
    periodo_vigencia = fields.Selection([
        ('years', _('Años')),
        ('months', _('Meses')),
        ('days', _('Días')),
    ], string='Período de Vigencia Mínima', default=False, copy=True, tracking=True)
    vigencia_minima = fields.Integer(string=_("Vigencia Mínima"), default=False, copy=True, tracking=True)

    caducidad_limitada_por_documento = fields.Boolean('¿Limitada por otro documento?', default=False, copy=True, index=True, tracking=True)
    caducidad_documento_ids = fields.Many2many(
        "tramite.documento",
        "doc_doc_limita_caducidad",
        "doc_id",
        "doc_limita_caducidad_id",
        string=_("Otros Documentos"),
        tracking=True)

    action_report_id = fields.Many2one("ir.actions.report",
        string=_("Reportes"),
        domain="[('model','=', model_model)]",
        tracking=True)

    es_inspeccion = fields.Boolean(string=_('Es inspección?'), default=False, copy=True, tracking=True)
    tiene_extension = fields.Boolean('Tiene Extensión/Prórroga', default=False, copy=True, tracking=True)
    tiene_endoso = fields.Boolean('Tiene Endoso', default=False, copy=True, tracking=True)
    tiene_condicional = fields.Boolean('Tiene Condicional', default=False, copy=True, tracking=True)
    endoso_ids = fields.One2many("tramite.documento.endoso", "servicio_id", string="Endoso", tracking=True)
    factor = fields.Boolean('Tiene factor?', default=False)
    factor_descripcion = fields.Char('Descripción factor')
    tipo_permiso_provisional_id = fields.Many2one('permar.permiso.provisional.embarque.tipo', string='Tipo permiso provisional', tracking=True)

    def get_tipo_inspeccion_is_valid(self, tipo):
        self.ensure_one()
        if not self.es_inspeccion:
            return False
        return tipo in ['ini', 'rei'] or (tipo == 'end' and self.tiene_endoso) or (tipo == 'ext' and self.tiene_extension)

    @api.onchange('caduca')
    def _onchange_caduca(self):
        if not self.caduca:
            self.periodo_caducidad = self.caducidad = False
            self.periodo_vigencia = self.vigencia_minima = False
            self.caducidad_limitada_por_documento = False
            if self.caducidad_documento_ids:
                # (5:CLEAR, ID, 0) Remove relation, keep records
                self.write({'caducidad_documento_ids': [(5, 0, 0)]})

    @api.onchange("model_id")
    def _onchange_model_id(self):
        if not self.model_id:
            self.action_report_id = False
        else:
            action_report_ids = []
            domain=[('model','=', self.model_model)]
            action_report_ids = self.env['ir.actions.report'].search(domain)
            if len(action_report_ids) == 1:
                self.action_report_id = action_report_ids.id
            else:
                return {'domain': {'action_report_id': [('id', 'in', action_report_ids.ids)]}}

    def calcular_requisitos(self, **kwargs):
        requisitos = []
        # kwargs must have nave_id, jerarquia_id, etc. only id (int), not object/record

        # Convert kwargs from a dict of ids (int) to a list of objects/records
        field_to_model = {
            'tipo_documento_id': 'sigmap.documento.tipo',
            'personal_maritimo_id': 'personal.maritimo',
            'jerarquia_id': 'personal.maritimo.catalogo.jerarquia',
            'curso_id': 'personal.maritimo.catalogo.curso',
        }

        for field, model in field_to_model.items():
            kwargs[field] = self.env[model].browse(kwargs[field])
        for requisito in self.requisito_ids:
            model_requisito = requisito.documento_requerido_id.model_id
            if not model_requisito:
                es_completado = False
                doc_name = ''
            else:
                kwargs['model'] = model_requisito.model
                doc, es_completado = self.env[model_requisito.model].validar_como_requerido(**kwargs)
                doc_name = doc.name if doc else ''

            requisitos.append({
                'id': requisito.documento_requerido_id.id,
                'name': requisito.documento_requerido_id.name,
                'obligatorio': requisito.obligatorio,
                'es_completado': es_completado,
                'doc_encontrado': doc_name,
            })

        return requisitos


class TramiteDocumentoEndoso(models.Model):
    _name = "tramite.documento.endoso"
    _description = "Endoso"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    servicio_id = fields.Many2one("tramite.documento", string=_("Documento"), tracking=True)
    meses = fields.Integer(string=_("Meses - próximo Endoso"), default=22,tracking=True)
    meses_limite = fields.Integer(string=_("Meses Límite - próximo Endoso"), default=26, tracking=True)


class TramiteDocumentoReparto(models.Model):
    _name = "tramite.documento.reparto"
    _description = "Tipo de documento del trámite"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    servicio_id = fields.Many2one("tramite.documento", string=_("Documento requiriente"), tracking=True)
    reparto_id = fields.Many2one("sigmap.reparto", string=_("Reparto"), tracking=True)

# class TramiteDocumentoTipo(models.Model):
#     _name = "tramite.documento.tipo"
#     _description = "Tipo de documento del trámite"
#     _inherit = ["mail.thread", "mail.activity.mixin"]

#     name = fields.Char(string=_('Nombre'))
#     active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)


class TramiteDocumentoRequisito(models.Model):
    _name = "tramite.documento.requisito"
    _description = "Requisitos del documento del trámite"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True
    )
    name = fields.Char(related='documento_requerido_id.name')
    documento_requerido_id = fields.Many2one("tramite.documento", string=_("Documento requerido"), domain = "[('tipo_documento_id', '=', tipo_documento_id)]", tracking=True)
    servicio_id = fields.Many2one("tramite.documento", string=_("Documento requiriente"), tracking=True)
    tipo_documento_id = fields.Many2one(related='servicio_id.tipo_documento_id', string=_("Tipo Documento"), tracking=True, store=True)
    obligatorio = fields.Boolean(string=_("Obligatorio?"), default=True, tracking=True)
    company_type = fields.Selection([
            ("person","Natural"),
            ("company","Jurídica"),
        ], string=_("Tipo de Persona"), tracking=True)
