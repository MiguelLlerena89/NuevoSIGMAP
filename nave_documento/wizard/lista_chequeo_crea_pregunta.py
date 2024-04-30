from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import json

class ListaChequeo(models.Model):
    _inherit = 'lista.chequeo'

    def button_crea_edita_pregunta(self):
        self.ensure_one()
        if not self.id or len(self.grupo_pregunta_ids) == 0:
            raise ValidationError('Antes de crear preguntas, defina los grupos y guarde la lista de Chequeo.')
        ctx = dict(
            default_lista_chequeo_id = self.id,
        )
        action = self.env['ir.actions.actions']._for_xml_id('nave_documento.action_crea_edita_pregunta_wizard')
        action.update({
            'context': ctx
        })
        return action


class CreaEditaPregunta(models.TransientModel):
    _name = 'lista.chequeo.pregunta.wizard'
    _description = _("Agrega/Modifica Preguntas")

    lista_chequeo_id = fields.Many2one(
        'lista.chequeo',
        requiered=True,
        string='lista_chequeo')

    crear_editar_op = fields.Selection([
            ('crear', _('Crear')),
            ('editar', _('Editar')),
            ('borrar',_('Borrar'))
        ], default='crear',
        string=_('crear/Editar'))

    grupo_id = fields.Many2one(
        'lista.chequeo.grupo',
        domain="[('lista_chequeo_id','=',lista_chequeo_id)]",
        string=_('Grupo'))

    grupo_pregunta_ids = fields.One2many(related='grupo_id.pregunta_ids', readonly=True)

    pregunta_id_domain = fields.Char(
        string=_('pregunta_id_domain'),
        compute='_compute_pregunta_id_domain',
        store=True,
        precompute=True)

    pregunta_id = fields.Many2one(
        'lista.chequeo.grupo.pregunta',
        string=_('Pregunta'))

    pregunta_child_ids = fields.One2many(related='pregunta_id.child_ids', readonly=True)
    pregunta_has_child_ids = fields.Boolean(related='pregunta_id.has_child_ids', readonly=True)

    is_parent = fields.Boolean(
        string=_('Es parte de otra?'),
        default=False)

    parent_id = fields.Many2one(
        'lista.chequeo.grupo.pregunta',
        domain="[('grupo_id','=',grupo_id),('parent_id','=',False)]",
        string=_('Principal'))

    parent_child_ids = fields.One2many(related='parent_id.child_ids', readonly=True)

    sequence = fields.Integer(_('Orden'))

    name = fields.Char(
        string=_('Texto Corto'))

    texto = fields.Char(
        string=_('Texto Adicional'))

    puntaje_no_satisfactorio = fields.Integer('Puntaje')

    porcentaje_si_hijo = fields.Float('Porcentaje')

    def _clean_fields_pregunta(self):
        self.sequence = self.name = self.texto = False
        self.puntaje_no_satisfactorio = self.porcentaje_si_hijo = False

    @api.onchange('crear_editar_op')
    def _onchange_crear_editar_op(self):
        self.ensure_one()
        if self.crear_editar_op != 'crear':
            self.grupo_id = False
            self.is_parent = self.parent_id = False
        self.pregunta_id = False
        self._clean_fields_pregunta()

    @api.onchange('grupo_id')
    def _onchange_grupo_id(self):
        self.ensure_one()
        if self.crear_editar_op != 'crear' or \
            ((self.is_parent and self.parent_id) and \
            self.grupo_id.id != self.parent_id.grupo_id.id):
            self.is_parent = self.parent_id = False
        self.pregunta_id = False
        self._clean_fields_pregunta()

    @api.onchange('is_parent')
    def _onchange_is_parent(self):
        self.ensure_one()
        if self.crear_editar_op != 'crear' or not self.is_parent:
            self.parent_id = False
        self.pregunta_id = False
        self._clean_fields_pregunta()

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        self.ensure_one()
        if self.crear_editar_op != 'crear':
            self.pregunta_id = False
            self._clean_fields_pregunta()

    def _load_fields_pregunta(self):
        return [
            'is_parent',
            'parent_id',
            'sequence',
            'name',
            'texto',
            'puntaje_no_satisfactorio',
            'porcentaje_si_hijo'
        ]

    @api.onchange('pregunta_id')
    def _onchange_pregunta_id(self):
        if not self.pregunta_id:
            self._clean_fields_pregunta()
        else:
            pregunta_record = self.pregunta_id
            for fieldname in self._load_fields_pregunta():
                self[fieldname] = pregunta_record[fieldname]

    @api.depends('grupo_id','is_parent','parent_id')
    def _compute_pregunta_id_domain(self):
        for rec in self:
            domain = []
            if rec.grupo_id:
                domain.append(('grupo_id','=',rec.grupo_id.id))
            if rec.is_parent and rec.parent_id and rec.parent_id.id:
                domain.append(('parent_id', '=', rec.parent_id.id))
            if not rec.is_parent:
                domain.append(('is_parent','=',rec.is_parent))

            if len(domain) == 0:
                domain = [()]
            rec.pregunta_id_domain = json.dumps(domain)


    def _check_wizard_fields(self):
        """def valid_required_fields(self):
            if not self.name or not self.sequence \
                or self.is_parent and (not self.parent_id or not self.porcentaje_si_hijo) \
                or not self.is_parent and not self.puntaje_no_satisfactorio:
                return True
            return False

        self.ensure_one()
        if (self.crear_editar_op in ['editar', 'borrar'] and not self.pregunta_id):# \
            #or not self.valid_required_fields():
            raise ValidationError(_('Error al guardar. Revise los parámetros ingresados'))"""
        pass

    def _crear_nuevo(self):
        ctx = dict(
            default_lista_chequeo_id=self.lista_chequeo_id.id,
            default_crear_editar_op='crear',
            default_grupo_id=self.grupo_id.id,
            default_is_parent=self.is_parent)

        if self.is_parent:
            ctx['default_parent_id'] = self.parent_id.id

        action = self.env["ir.actions.actions"]._for_xml_id("nave_documento.action_crea_edita_pregunta_wizard")
        action.update({
            'context': ctx,
            })

        return action

    def _create_update_pregunta(self, nuevo=False):
        pregunta_model = self.env['lista.chequeo.grupo.pregunta']
        pregunta = False
        vals = dict(
            lista_chequeo_id=self.lista_chequeo_id.id,
            grupo_id=self.grupo_id.id,
            sequence=self.sequence,
            name=self.name,
            texto=self.texto,
            is_parent=self.is_parent,
            porcentaje_si_hijo=self.porcentaje_si_hijo,
            puntaje_no_satisfactorio=self.puntaje_no_satisfactorio
        )
        if self.parent_id:
            vals['parent_id'] = self.parent_id.id
        if not self.parent_id and "default_parent_id" in self.env.context.keys():
            vals['parent_id'] = False

        try:
            mode = self.crear_editar_op
            if mode == 'crear':
                pregunta = pregunta_model.create(vals)
            else:
                pregunta = pregunta_model.browse(self.pregunta_id.id)
                if mode == 'editar':
                    pregunta.write(vals)
                else:
                    pregunta.unlink()
        except Exception as err:
            err_msg = _('Error al guardar. Revise los parámetros ingresados') + f'\n{err}'
            raise ValidationError(err_msg)
            return False

        if nuevo:
            return self._crear_nuevo()

        return True

    def action_crea_edita_pregunta(self):
        self.ensure_one()
        return self._create_update_pregunta(nuevo=False)


    def action_crea_edita_pregunta_nuevo(self):
        self.ensure_one()
        return self._create_update_pregunta(nuevo=True)
