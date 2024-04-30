from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.fields import Command

import logging

_logger = logging.getLogger(__name__)

class Tramite(models.Model):
    _name = "tramite"
    _description = "Tramite"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = 'create_date'

    def _default_company(self):
        return self.env.user.company_id

    name = fields.Char(index=True, size=100)
    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True
    )
    servicio_id = fields.Many2one("tramite.documento",
        domain = "[('tipo_documento_id', '=', tipo_documento_id), ('emitido_por_dirnea', '=', True)]",
        string=_("Servicio"),
        required=False, tracking=True)
    model_model = fields.Char(related="servicio_id.model_model", string=_("Servicio"), tracking=True)
    requisito_ids = fields.One2many(
        "tramite.requisito",
        "tramite_id",
        string="Requisitos",
        tracking=True
    )
    rubro_ids = fields.One2many("tramite.rubro", "tramite_id", "Rubro", tracking=True, compute="_compute_rubro_ids", store=True)
    fecha_inicio = fields.Date(
        string="Fecha inicio",
        index=True,
        copy=False,
        tracking=True,
        default=fields.Date.today
    )
    fecha_caducidad = fields.Date(
        string="Fecha caducidad",
        compute="_calcular_periodo_caducidad",
        store=True,
        readonly=True,
        index=True,
        copy=False,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Por revisar"),
            ("payable", "Por pagar"),
            ("invoiced", "Facturado"),
            ("in_process", "En trámite"),
            ("posted", "Tramitado"),
            #("sent", "Entregado"),
            ("rechazado", "Rechazado"),
            ("pausado", "Pausado"),
        ],
        string="Status",
        copy=False,
        tracking=True,
        default="draft",
    )
    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Order Reference",
        readonly=True, ondelete="cascade", index=True, copy=False, store=True)
    tipo_documento_id = fields.Many2one(related='order_id.tipo_documento_id')
    reparto_id = fields.Many2one(related='order_id.reparto_id')
    personal_maritimo_id = fields.Many2one(
        related="order_id.beneficiario_id",
        store=True,
        tracking=True
    )
    beneficiario_nave_id = fields.Many2one(
        related="order_id.beneficiario_nave_id",
        string=_('Beneficiario'),
        store=True,
        tracking=True
    )
    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Nave'),
        related="order_id.nave_id",
        store=True,
        tracking=True)

    currency_id = fields.Many2one(
        #related="pricelist_id.currency_id",
        #depends=["pricelist_id"],
        store=True, ondelete="restrict")
    reimpresion = fields.Boolean(
        string=_("Reimpresión?"),
        tracking=True, default=False)
    completado_requisitos = fields.Boolean(
        string=_("Requisitos completados?"),
        compute="_compute_completado_requisitos",
        readonly=False,
        tracking=True, store=True)
    completado_cursos = fields.Boolean(
        string=_("Cursos completados?"),
        compute="_compute_completado_requisitos",
        readonly=False,
        tracking=True, store=True)
    completado = fields.Boolean(
        string=_("Completado?"),
        compute="_compute_completado",
        readonly=False,
        tracking=True, store=True)
    allowed_jerarquia_ids = fields.Many2many(
        comodel_name="personal.maritimo.catalogo.jerarquia",
        compute="_compute_allowed_jerarquia_ids"
    )
    mostrar_jerarquia = fields.Boolean(string=_("Mostrar jerarquia"), tracking=True,
        compute="_compute_mostrar_campos_permar"
    )
    documento_entregado = fields.Boolean(string=_("Documento entregado"), tracking=True)
    mostrar_curso = fields.Boolean(string=_("Mostrar curso"), tracking=True,
        compute="_compute_mostrar_campos_permar"
    )
    jerarquia_id = fields.Many2one("personal.maritimo.catalogo.jerarquia", string=_("Jerarquia"), tracking=True,
        domain="[('id', 'in', allowed_jerarquia_ids)]"
    )
    clasificacion_id = fields.Many2one(
        "personal.maritimo.clasificacion",
        string=_("Clasficación"),
        tracking=True)
    requisito_curso_ids = fields.One2many(
        "tramite.requisito.curso",
        "tramite_id",
        string="Cursos requeridos",
        tracking=True
    )
    allowed_curso_ids = fields.Many2many('personal.maritimo.catalogo.curso', compute="_compute_allowed_curso_ids")
    curso_id = fields.Many2one('personal.maritimo.catalogo.curso', tracking=True,
        domain="[('id', 'in', allowed_curso_ids)]"
    )
    validar_cursos_omi = fields.Boolean(
        related='servicio_id.validar_cursos_omi'
    )
    validar_cursos_formacion = fields.Boolean(
        related='servicio_id.validar_cursos_formacion'
    )
    cantidad = fields.Float(string="Cantidad")
    factor = fields.Boolean(
        related='servicio_id.factor'
    )
    factor_descripcion = fields.Char(
        related='servicio_id.factor_descripcion'
    )

    tipo_trafico_id = fields.Many2one(
        "tipo.trafico",
        string="Tipo de tráfico",
        tracking=True
    )

    es_inspeccion = fields.Boolean(related="servicio_id.es_inspeccion", string=_('Es inspección?'))
    tipo_inspeccion = fields.Selection(
        [
            ('ini', 'Inicial o Renovación'),
            ('rei', 'Reinspección'),
            ('end', 'Endoso'),
            ('ext', 'Extensión'),
        ],
        string=_('Tipo Inspección'), default=False, tracking=True)
    pkey_sigmap = fields.Char(string='Pkey del sigmap anterior', tracking=True)
    tipo_permiso_id = fields.Many2one(related="servicio_id.tipo_permiso_provisional_id")

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    resource_ref = fields.Reference(string='Record', selection='_selection_target_model')

    nave_persona = fields.Char(compute='_compute_persona_nave', string=_('Nave/Persona'), store=True)

    @api.depends('nave_id', 'personal_maritimo_id')
    def _compute_persona_nave(self):
        for rec in self:
            related_field = rec.nave_id if rec.nave_id else rec.personal_maritimo_id
            name_get = related_field.name_get()
            name = related_field.name

            rec.nave_persona = name_get[0][1] \
                if name_get and len(name_get)>0 and name_get[0] and len(name_get[0])>1 and name_get[0][1] \
                else name

    @api.depends("servicio_id")
    def _compute_mostrar_campos_permar(self):
        for rec in self:
            rec.mostrar_jerarquia = False
            rec.mostrar_curso = False
            if rec.servicio_id and rec.tipo_documento_id.id == self.env.ref('base_sigmap.gente_mar').id:
                if rec.servicio_id.validar_cursos_formacion:
                    rec.mostrar_jerarquia = True
                if rec.servicio_id.validar_cursos_omi:
                    rec.mostrar_curso = True

    @api.depends("completado_requisitos", "completado_cursos")
    def _compute_completado(self):
        for record in self:
            record.completado = record.completado_requisitos and record.completado_cursos

    @api.depends("personal_maritimo_id", "servicio_id")
    def _compute_allowed_curso_ids(self):
        for record in self:
            if record.personal_maritimo_id:
                if record.personal_maritimo_id.cursos_ids:
                    ids = []
                    cursos = False
                    if record.validar_cursos_formacion:
                        cursos = record.personal_maritimo_id.cursos_ids.filtered(lambda c: c.tipo_curso == "formacion")
                    if record.validar_cursos_omi:
                        cursos = record.personal_maritimo_id.cursos_ids.filtered(lambda c: c.tipo_curso == "capacitacion")
                    if cursos:
                        for j in cursos:
                            ids.append(j.curso_id.id)
                        domain = [('id', 'in', ids)]
                        if len(ids) > 0:
                            record.allowed_curso_ids = self.env["personal.maritimo.catalogo.curso"].search(domain)
                        continue
            record.allowed_curso_ids = False

    @api.depends("personal_maritimo_id")
    def _compute_allowed_jerarquia_ids(self):
        for record in self:
            if record.personal_maritimo_id.jerarquia_ids:
                ids = []
                for j in record.personal_maritimo_id.jerarquia_ids:
                    ids.append(j.jerarquia_id.id)
                    # Revisa si la jerarquía tiene padre/superior
                    if j.jerarquia_id.jerarquia_id:
                        ids.append(j.jerarquia_id.jerarquia_id.id)
                domain = [('id', 'in', ids)]
                if len(ids) > 0:
                    record.allowed_jerarquia_ids = self.env["personal.maritimo.catalogo.jerarquia"].search(domain)
            else:
                record.allowed_jerarquia_ids = False

    # @api.depends('fecha_inicio', 'servicio_id')
    # def _calcular_periodo_caducidad(self):
    #     for rec in self:
    #         if rec.fecha_inicio and rec.servicio_id.caducidad:
    #             rec.fecha_caducidad = rec.fecha_inicio + relativedelta(years=+rec.servicio_id.caducidad)

    @api.depends('fecha_inicio', 'servicio_id')
    def _calcular_periodo_caducidad(self):
        for rec in self:
            if rec.fecha_inicio and rec.servicio_id.caducidad:
                periodo_caducidad = str(rec.servicio_id.periodo_caducidad)
                caducidad = int(rec.servicio_id.caducidad)
                rec.fecha_caducidad = rec.fecha_inicio + relativedelta(**{periodo_caducidad:+ int(caducidad)}) #(periodo_caducidad=+caducidad)

    def check_requisitos_completados(self):
        incompleto = self.requisito_ids.filtered(lambda c: not c.completado and c.obligatorio)
        incompleto_cursos = self.requisito_curso_ids.filtered(lambda c: not c.completado)
        if len(list(incompleto)) == 0:
            completado_requisitos = True
        else:
            completado_requisitos = False

        if len(list(incompleto_cursos)) == 0:
            completado_cursos = True
        else:
            completado_cursos = False

        return completado_cursos, completado_requisitos

    @api.depends("servicio_id", "requisito_ids", "requisito_curso_ids")
    def _compute_completado_requisitos(self):
        self.completado_cursos, self.completado_requisitos = self.check_requisitos_completados()

    def _get_tramite_es_tipo_nave(self):
        tipo_nave = self.env.ref('base_sigmap.nave')
        return tipo_nave and self.tipo_documento_id and (self.tipo_documento_id.id == tipo_nave.id)

    @api.onchange("servicio_id")
    def _onchange_servicio_id_para_tipo_inspeccion(self):
        if self._get_tramite_es_tipo_nave() and self.servicio_id and self.es_inspeccion and \
            (not self.tipo_inspeccion or self.tipo_inspeccion != "ini"):
            self.tipo_inspeccion = "ini"

    @api.onchange('tipo_inspeccion')
    def _onchange_tipo_inspeccion(self):
        if self.servicio_id and self._get_tramite_es_tipo_nave() and self.tipo_inspeccion and not self.servicio_id.get_tipo_inspeccion_is_valid(self.tipo_inspeccion):
            raise ValidationError(_(f'El documento o servicio {self.servicio_id.name} no tiene tipo de inspección seleccionado configurado. Contacte a Soporte Técnico'))

    @api.onchange("curso_id")
    def _onchange_curso_id(self):
        # Check requisitos de la jerarquía
        #if self.requisito_curso_ids:
        #    self.write({"requisito_curso_ids": [(5,0,0)]})
        if self.curso_id:
            self.write({"requisito_curso_ids": [(0, 0, {
                    "curso_id": self.curso_id.id,
                })]})

    OPERADORES = {
         'igual': '=',
         'no_igual': '!=',
         'mayor': '>',
         'menor': '<',
         'mayor_igual': '>=',
         'menor_igual': '<=',
         }
    CONDICIONALES_NAVES = ['trb', 'eslora', 'nave_tipo_grupo_id', 'nave_tipo_id', 'nave_origen_id', 'nave_servicio_id', 'nave_zona_id', 'tipo_trafico_id']
    CONDICIONALES_PERMAR = ['jerarquia']

    def check_amount(self):
        rubro_doc = []

        tipo_nave_id = self.env.ref('base_sigmap.nave').id
        nave = False

        if self.tipo_documento_id.id in [tipo_nave_id, self.env.ref('base_sigmap.trafico_maritimo').id] and self.nave_id:
            nave = self.nave_id

        rubros = self.servicio_id.rubro_ids
        if  self.es_inspeccion and self.tipo_inspeccion:
            rubros = [rubro for rubro in rubros if rubro.tipo_inspeccion in [self.tipo_inspeccion, False]]
        for rubro in rubros:
            # Revisar servicio elegido y ver cada rubro
            # Revisar si existe tarifas para este rubro activas y actuales
            # Buscar reglas en base a condiciones del trámite
            # Revisar si existen tarifas anteriores con incremento
            # usar ese valor y calcular el incremento
            tarifas = rubro.tarifa_ids.filtered(lambda a: a.active and a.tarifario_id.active)
            if rubro.rubro_maestro_id:
                tarifas = rubro.rubro_maestro_id.tarifa_ids.filtered(lambda a: a.active and a.tarifario_id.active)

            for tarifa in tarifas:
                #En modelo tarifario.tarifa get_tarifa: revisa todos los valor_tarifa.monto o monto de la tarifa
                # También puedo revisar el monto del rubro maestro
                data = {
                    'product_id': rubro.id,
                }
                monto, minimo, maximo = tarifa.get_monto_tarifa()

                if tarifa.tipo ==  'constante':
                    data['monto'] = monto
                    if tarifa.monto_base > 0:
                        data['monto'] = monto + tarifa.monto_base
                elif tarifa.tipo ==  'porcentaje':
                    # tipo:porcentaje solo trabaja con variable:sbu
                    if 'sbu' in tarifa.variable:
                        params = self.env['ir.config_parameter'].sudo()
                        sbu = params.get_param("tramite.sbu")
                        if sbu:
                            data['monto'] = monto * float(sbu) / 100
                elif tarifa.tipo ==  'formula':
                    # tipo:formula solo trabaja para naves
                    if self.tipo_documento_id.id == tipo_nave_id:
                        variable = tarifa.variable
                        resultado = monto * nave[variable]
                        if tarifa.monto_base > 0:
                            resultado = resultado + tarifa.monto_base
                        if resultado <= minimo:
                            data['monto'] = minimo
                        if maximo > 0 and resultado >= maximo:
                            data['monto'] = maximo
                        else:
                            data['monto'] = resultado
                if rubro.porcentaje_maestro:
                    data['monto'] = data['monto'] * rubro.porcentaje_maestro / 100

                if nave and nave.en_fletamento_o_contrato():
                    recargo_maximo = False

                    rubro_con_recargo = rubro.rubro_maestro_id if rubro.rubro_maestro_id else rubro

                    if rubro_con_recargo.porcentaje_recargo_nave_int:
                        data['monto'] = (data['monto'] * (100 + rubro_con_recargo.porcentaje_recargo_nave_int)) / 100
                        recargo_maximo = rubro_con_recargo.monto_max_nave_int

                        if recargo_maximo and recargo_maximo > 0.0 and (recargo_maximo < data['monto']):
                            data['monto'] = recargo_maximo

                if not tarifa.regla_ids:
                    rubro_doc.append((0, 0, data))
                    break

                cumple_regla = False
                if self.tipo_documento_id.id == self.env.ref('base_sigmap.gente_mar').id:
                    if tarifa.regla_ids and self.jerarquia_id:
                        cumple_regla = self.env['rubro.regla'].search(
                            [
                                ('rubro_tarifa_id', '=', tarifa.id),
                                ('active', '=', True),
                                ('variable', '=', 'jerarquia'),
                                ('resource_ref', '=', 'personal.maritimo.catalogo.jerarquia,'+str(self.jerarquia_id.id)),
                            ]
                        )
                elif self.tipo_documento_id.id in [self.env.ref('base_sigmap.trafico_maritimo').id, tipo_nave_id]:
                    nave_domain = [('id', '=', nave.id)]
                    for regla in tarifa.regla_ids:
                        if regla.variable in self.CONDICIONALES_NAVES:
                            if regla.resource_ref:
                                nave_domain.append((regla.variable, self.OPERADORES[regla.tipo], regla.resource_ref.id))
                            else:
                                nave_domain.append((regla.variable, self.OPERADORES[regla.tipo], regla.valor))
                    cumple_regla = self.env['nave.nave'].search(nave_domain)

                if cumple_regla:
                    rubro_doc.append((0, 0, data))
                    break
        return rubro_doc

    @api.onchange("jerarquia_id")
    def _onchange_jerarquia_id(self):
        # Check requisitos de la jerarquía
        if self.requisito_curso_ids:
            self.write({"requisito_curso_ids": [(5,0,0)]})
        if self.jerarquia_id:
            requisitos = []
            if self.validar_cursos_omi:
                for jer_req in self.jerarquia_id.requisito_ids:
                    requisitos.append((0, 0, {
                        "curso_id": jer_req.curso_id.id,
                    }))
            if self.validar_cursos_formacion:
                curso = self.env['personal.maritimo.catalogo.curso'].search([
                    ("jerarquia_id", "=", self.jerarquia_id.id)
                    ], limit=1)
                if curso:
                    self.curso_id = curso.id
            self.write({"requisito_curso_ids": requisitos})

    @api.depends("servicio_id", "jerarquia_id", "tipo_inspeccion")
    def _compute_rubro_ids(self):
        for rec in self:
            rec.write({"rubro_ids": [(5,0,0)]})
            if not rec.order_id.tipo_documento_id:
                raise ValidationError(_('Debe seleccionar el tipo de solicitud'))
            if rec.servicio_id:
                rubro_doc = rec.check_amount()
                rec.write({
                    "rubro_ids": rubro_doc,
                    })

    @api.onchange("servicio_id")
    def _onchange_documento_id(self):
        if not self.order_id.tipo_documento_id:
            raise ValidationError(_('Debe seleccionar el tipo de solicitud'))
        self.jerarquia_id = False
        self.curso_id = False
        self.write({"requisito_ids": [(5,0,0)]})
        if self.servicio_id:
            self._default_requisitos()
        if self.servicio_id and self.personal_maritimo_id and self.mostrar_jerarquia:
            self.jerarquia_id = self.personal_maritimo_id.jerarquia_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code("tramite_sequence_code")
        return super().create(vals_list)

    def action_iniciar_tramite(self):
        self.completado_cursos, self.completado_requisitos = self.check_requisitos_completados()
        if self.completado_cursos and self.completado_requisitos:
            self.state = "in_process"
        else:
            raise ValidationError(_('No se ha completado la lista de requisitos'))

    def action_terminar_tramite(self):
        if self.state == "in_process":
            self.state = "posted"
        else:
            raise ValidationError(_('No se ha completado la lista de requisitos'))

    def action_pausar_tramite(self):
        if self.state == "in_process":
            self.state = "pausado"
        else:
            raise ValidationError(_('No puede pausar el trámite si no esta iniciado.'))

    def _default_requisitos(self):
        requisitos_doc = []
        if self.servicio_id.requisito_ids:
            requisitos = []
            tipo_persona = self.order_id.partner_id.company_type if not self.personal_maritimo_id else self.personal_maritimo_id.company_type
            requisitos = self.servicio_id.requisito_ids.filtered(lambda r: r.company_type == tipo_persona or r.company_type == False)
            if requisitos:
                for req in requisitos.sorted():
                    requisitos_doc.append((0, 0, {
                        "requisito_id": req.id,
                    }))
                self.write({
                     "requisito_ids": requisitos_doc
                    })
    # Validar si puede realizar trámite

    def action_send_email(self):
        self.ensure_one()
        mail_template = self.env.ref('tramite.email_template_tramite')
        mail_template.send_mail(self.id, force_send=True)


    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            self.action_send_email()


class TramiteRequisitoCurso(models.Model):
    _name = "tramite.requisito.curso"
    _description = "Requisitos cursos"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)
    curso_id = fields.Many2one("personal.maritimo.catalogo.curso", string=_("Curso"), tracking=True)
    personal_maritimo_curso_id = fields.Many2one(
        "personal.maritimo.curso",
        string=_("Cursos de personas"),
        compute="_compute_curso_existente",
        inverse="_inverse_curso_edit",
        domain="[('curso_id', '=', curso_id), ('personal_maritimo_id', '=', personal_maritimo_id)]",
        tracking=True)

    tramite_id = fields.Many2one("tramite", string=_("Tramite"), tracking=True)
    personal_maritimo_id = fields.Many2one(related="tramite_id.personal_maritimo_id", string=_("Tramite"), tracking=True)
    completado = fields.Boolean(string=_("Completado?"), default=False, tracking=True, store=True)

    @api.depends('curso_id')
    def _compute_curso_existente(self):
        for line in self:
            if line.curso_id:
                curso_persona = self.env['personal.maritimo.curso'].search([
                    ("personal_maritimo_id", "=", line.personal_maritimo_id.id ),
                    ("curso_id", "=", line.curso_id.id ),
                    ], limit=1)
                if curso_persona:
                    line.personal_maritimo_curso_id = curso_persona.id
                    line.completado = True
                else:
                    line.personal_maritimo_curso_id = False
                    line.completado = False

    def _inverse_curso_edit(self):
        pass


class TramiteRequisito(models.Model):
    _name = "tramite.requisito"
    _description = "Requisitos trámite"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    completado = fields.Boolean(string=_("Completado?"),
        default=False, store=True, tracking=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)
    requisito_id = fields.Many2one("tramite.documento.requisito", string=_("Requisito"), tracking=True)
    documento_requerido_id = fields.Many2one(related="requisito_id.servicio_id", string=_("Documento del requisito"), tracking=True)
    documento_req_id = fields.Many2one(
        "tramite.documento",
        related="requisito_id.servicio_id",
        string=_("Documento requerido"),
        tracking=True)
    tramite_id = fields.Many2one("tramite", string=_("Tramite"), tracking=True)
    obligatorio = fields.Boolean(related='requisito_id.obligatorio')
    completado = fields.Boolean(string=_("Completado"), default=False, tracking=True)
    personal_maritimo_id = fields.Many2one(related="tramite_id.personal_maritimo_id", string=_("Tramite"), tracking=True)
    upload_file = fields.Binary(string='Archivo')
    upload_file_filename = fields.Char(string='Nombre de archivo')
    name = fields.Char(string="Referencia")


class TramiteRubro(models.Model):
    _name = "tramite.rubro"
    _description = "Rubros"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True
    )
    tramite_id = fields.Many2one("tramite", string=_("Tramite"), tracking=True)
    currency_id = fields.Many2one(
        related="tramite_id.currency_id",
        depends=["tramite_id.currency_id"],
        store=True, precompute=True)
    product_id = fields.Many2one("product.template", string=_("Rubro"), tracking=True)
    monto = fields.Monetary(
        string="Monto",
        store=True)
