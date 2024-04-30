from odoo import api, fields, models, _

from cryptography.hazmat.primitives.serialization import pkcs12
import cryptography
import base64

class SumillaUsuario(models.Model):
    _name = 'sumilla.usuario'
    _description = 'Sumilla Usuario'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sumilla_user_id = fields.Many2one('res.users', string="Usuario", required=True, tracking=True, copy=False)
    sumilla = fields.Char('Sumilla', required=True)

    def name_get(self):
        self.read(['sumilla_user_id'])
        return [(rec.id, '%s - %s' % (rec.sumilla, rec.sumilla_user_id.name))
            for rec in self]

    _sql_constraints = [
        ('sumilla_usuario_uniq', 'unique (sumilla_user_id)', 'Sumilla para usuario existente!!')
    ]


class PersonaAutoridad(models.Model):
    _name = 'persona.autoridad'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_sumilla(self):
        return self.env['sumilla.usuario'].search([('sumilla_user_id.id', '=', self.autoridad_user_id.id)], limit=1).id

    def _default_company(self):
        return self.env.user.company_id

    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        default=_default_company,
        tracking=True)

    autoridad_user_id = fields.Many2one('res.users', string="Usuario", tracking=True, copy=False)
    name = fields.Char(related="autoridad_user_id.name")
    certificate = fields.Binary('Firma electronica', tracking=True, copy=False)
    certificate_filename = fields.Char(string="File Name", tracking=True, copy=False)
    image_firma = fields.Image('Foto firma')

    user_id = fields.Many2one(
        'res.users', string='Usuario', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)

    rango_id = fields.Many2one('tipo.rango', string='Rango')
    rango_abreviatura = fields.Char(related='rango_id.abreviatura', string='Rango abreviatura')
    texto_firma = fields.Char(string='Texto firma')
    texto_cargo = fields.Char(string='Texto cargo')
    #sumilla = fields.Char(related='autoridad_user_id.sumilla')
    sumilla_id = fields.Many2one('sumilla.usuario', string="Sumilla",)
    observacion_firma = fields.Html(string="Firma Contexto")
    active = fields.Boolean(_('Active?'), default=True)

    @api.onchange("autoridad_user_id")
    def _onchange_autoridad_user_id(self):
        for rec in self:
            if rec.autoridad_user_id:
                rec.sumilla_id = self._get_sumilla()
            else:
                rec.sumilla_id = False
