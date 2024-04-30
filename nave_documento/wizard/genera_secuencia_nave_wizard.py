from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class NaveDocumentoMatricula(models.Model):
    _inherit = 'nave.documento.matricula'

    def button_generar_matricula_nave_wizard(self):
        self.ensure_one()
        ctx = dict(
            default_tipo_secuencia_id = self.env.ref("base_sigmap.matricula_nave").id,
            default_nave_matricula_id = self.id,
            default_nave_id = self.nave_id.id,
            default_nave_clase_matricula_id = self.nave_id.nave_clase_matricula_id.id,
            default_reparto_id = self.nave_id.reparto_id.id,
        )
        action = self.env["ir.actions.actions"]._for_xml_id("nave_documento.action_genera_secuencia_nave_wizard")
        action.update({
            'context': ctx,
            })
        return action

class GeneraSecuenciaNaveWizard(models.TransientModel):
    _name = 'genera.secuencia.nave.wizard'
    _description = 'Generar Secuencia Nave'

    tipo_secuencia_id = fields.Many2one('sigmap.secuencia.tipo',string='Tipo Secuencia', required=True)
    nave_matricula_id = fields.Many2one(
        'nave.documento.matricula',
        string=_('Matrícula nave'),
        readonly=True,
        index=True,
        copy=False,
        tracking=True)

    nave_clase_matricula_id = fields.Many2one(
        'nave.nave.clase.matricula',
        string=_('Registration Class'),
        required=True,
        index=True,
        copy=False,
        tracking=True)
    codigo = fields.Char(
        related='nave_clase_matricula_id.codigo',
        string='Código Clase Matrícula',
        tracking=True)

    reparto_id = fields.Many2one(
        'sigmap.reparto',
        string=_('Reparto'),
        required=True,
        index=True,
        copy=False,
        domain=lambda self: "[('codigo_matricula','not in', False),('tipo_id', '=', {})]".format(self.env.ref("base_sigmap.sigmap_reparto_tipo_capitania").id),
        tracking=True)
    codigo_matricula = fields.Char(
        related='reparto_id.codigo_matricula',
        string='Código Matrícula Reparto',
        tracking=True)

    nave_id = fields.Many2one(
        'nave.nave',
        string=_('Nave'),
        readonly=True,
        index=True,
        copy=False,
        tracking=True)

    matricula = fields.Char(
        string=_('Matrícula'),
        #required=True,
        index=True,
        copy=False,
        tracking=True)

    # @api.onchange("reparto_id")
    # def _onchange_reparto_id(self):
    #     documento_ids = False
    #     domain = []
    #     tipo_capitania_id = self.env.ref("base_sigmap.sigmap_reparto_tipo_capitania").id
    #     if tipo_capitania_id:
    #         domain = [
    #             #('company_id', '=', self.nave_matricula_id.company_id.id),
    #             ('tipo_id','=', tipo_capitania_id),
    #             ('codigo_matricula','not in', False),
    #         ]
    #         documento_ids = self.env['sigmap.reparto'].search(domain).ids
    #     return {'domain': {'reparto_id': [('id', 'in', documento_ids)]}}

    def _check_ship_registration_log(self):
        domain = [
            ('nave_id','=',self.nave_id.id),
            ('tramite_id','=',self.nave_matricula_id.documento_emitido_id.tramite_id.id),
            ('active','=',True),
        ]
        ckeck_ship_registration = self.env['nave.nave.matricula.bitacora'].search(domain, limit=1) #,('company_id','=', company.id)
        if ckeck_ship_registration:
            raise ValidationError(_('Ya existe una matrícula asociada a la nave %s generada con el trámite %s') % (self.nave_id.name, self.tramite_id.name))
        return True

    def _check_registration_sequence(self, company, search_code):
        for rec in self:
            ckeck_sequence = self.env['ir.sequence'].search([('code','ilike',search_code)], limit=1) #,('company_id','=', company.id)
            if not ckeck_sequence:
                raise ValidationError(_('Debe definir secuencial de matrículas para nave en reparto %s') % (rec.reparto_id.name))
        return True

    def _update_create_matricula_nave(self, company, matricula):
        for rec in self:
            matriculas = self.env['nave.nave.matricula.bitacora'].search([('company_id','=',company.id),('nave_id','=', self.nave_id.id)]).filtered(lambda c: c.active)
            if matriculas:
                matriculas.sudo().write({'active': False})
            nave_matricula_bitacora = self.env['nave.nave.matricula.bitacora'].create({
                'tramite_id': self.nave_matricula_id.documento_emitido_id.tramite_id.id,
                'fecha_tramite': fields.Datetime.now(),
                'tipo_tramite': '',
                'nave_id': self.nave_id.id,
                'order_id': self.nave_matricula_id.documento_emitido_id.tramite_id.order_id.id,
                'matricula': matricula,
                'company_id': company.id,
            }).id
        return nave_matricula_bitacora

    def action_genera_secuencia_nave(self):
        self.ensure_one()
        search_code = ''
        company = self.nave_matricula_id.company_id
        # tipo_secuencia_id = self.env.ref("base_sigmap.matricula_nave", raise_if_not_found=False)
        self._check_ship_registration_log()
        if self.tipo_secuencia_id:
            search_code = _('%s_%s_code') % (self.tipo_secuencia_id.name.lower().replace(' ','_'), self.reparto_id.siglas)
            self._check_registration_sequence(company, search_code)
            secure_sequence = self.env["ir.sequence"].next_by_code(search_code)
            matricula = '%s-%s-%s' % (self.codigo, self.codigo_matricula, secure_sequence)
            self.nave_id.sudo().write({'matricula': matricula, 'nave_clase_matricula_id': self.nave_clase_matricula_id.id, 'reparto_id': self.reparto_id.id})
            self._update_create_matricula_nave(company, matricula)
            self.nave_matricula_id.sudo().write({'pendiente_generar_matricula': False})
        else:
            raise ValidationError(_('No existe tipo de secuencial de matrículas para nave'))
        return True
