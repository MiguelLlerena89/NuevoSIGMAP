from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = ['personal.maritimo']

    reconocimiento_ids = fields.One2many(
        'permar.documento.reconocimiento.titulo', 'personal_maritimo_id', string='Reconocimientos de títulos',
        help="Reconocimientos de títulos de la persona")
    reconocimiento_count = fields.Integer(compute='_compute_reconocimiento_count')

    def _compute_reconocimiento_count(self):
        for partner in self:
            partner.reconocimiento_count = len(partner.reconocimiento_ids)

    def action_open_reconocimiento_titulo(self):
        self.ensure_one()
        return {
            'name': 'Reconocimientos de títulos',
            'type': 'ir.actions.act_window',
            'res_model': 'permar.documento.reconocimiento.titulo',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.reconocimiento_ids.ids)],
            'context':  {'default_personal_maritimo_id': self.id,}
        }


class ReconocimientoTitulo(models.Model):
    _name = "permar.documento.reconocimiento.titulo"
    _description = "Reconocimiento de títulos nacionales y extranjeros con países de convenio"
    _inherit = "documento.base.refrendo"

    curso_id = fields.Many2one(
        "personal.maritimo.catalogo.curso",
        string=_("Curso formación"),
        tracking=True)
    reparto = fields.Char(string=_("Reparto"), size=100, index=True, tracking=True)
    tipo_curso = fields.Selection(related='curso_id.tipo',
        store=True, readonly=False)
    tipo_curso_id = fields.Many2one(related='curso_id.tipo_curso_id',
        store=True, readonly=False)
    country_id = fields.Many2one(related='curso_persona_id.country_id', store=True,
        readonly=False)

    es_reconocimiento = fields.Boolean(related='curso_persona_id.es_reconocimiento', store=True, readonly=False)
    limitacion_ids = fields.One2many("permar.documento.reconocimiento.limitacion", "reconocimiento_id", "Limitaciones", tracking=True, readonly=False)
    numero_diploma = fields.Char(readonly=False)
    numero_formulario = fields.Char(readonly=False)
    fecha_emision_diploma = fields.Date(readonly=False)

    def _add_followers(self):
        if self.message_follower_ids:
            domain = [('partner_id', '=', self.env.user.partner_id.id),
                    ('res_id', '=', self.id),
                    ('res_model', '=', 'permar.documento.reconocimiento.titulo')
                ]
            print(domain)
            followers_id = self.env['mail.followers'].search(domain, limit=1)
            if not followers_id:
                reg = {
                        'res_id': self.id,
                        'res_model': 'permar.documento.reconocimiento.titulo',
                        'partner_id': self.env.user.partner_id.id,
                    }
                follower_id = self.env['mail.followers'].create(reg)
                print('follower_id')
                print(follower_id)

    def write(self, vals):
        res = super().write(vals)
        #self._add_followers()
        if res:
            if not self.curso_persona_id:
                curso = self.env['personal.maritimo.curso'].create({
                    "personal_maritimo_id": self.personal_maritimo_id.id,
                    "curso_id": self.curso_id.id,
                    "country_id": self.country_id.id,
                    "tipo_curso": self.tipo_curso,
                    "fecha_emision_diploma": self.fecha_emision_diploma,
                    "es_reconocimiento": True,
                    "numero_diploma": self.numero_diploma
                    })
                if curso:
                    self.curso_persona_id = curso.id
                    return True
        return res

    @api.model
    def create(self, vals):
        vals["name"] = self._get_seq_with_company("reconocimiento_titulo_code") #self.env["ir.sequence"].next_by_code("reconocimiento_titulo_code")
        res = super().create(vals)
        return res

    _sql_constraints = [
        ('documento_emitido_id_uniq', 'unique (documento_emitido_id)', 'Documento persona must be unique.')
    ]


class ReconocimientoLimitacion(models.Model):
    _name = "permar.documento.reconocimiento.limitacion"

    reconocimiento_id = fields.Many2one(
        "permar.documento.reconocimiento.titulo",
        string=_("Reconocimiento Título"),
        tracking=True)
    limitacion_id = fields.Many2one(
        "personal.maritimo.catalogo.limitacion",
        string=_("limitacion"),
        tracking=True)