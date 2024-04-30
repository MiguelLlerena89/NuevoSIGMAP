from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError, AccessError

class SigmapDocumentoSecuenciaTipo(models.Model):
    _name = "sigmap.documento.secuencia.tipo"
    _description = "Tipo de Secuencia por documentos en SIGMAP"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one('res.company', 'Company', index=True, default=lambda self: self.env.company.id)
    name = fields.Char(string=_('Descripción Secuencia'))
    tipo_secuencia_id = fields.Many2one(
        'sigmap.secuencia.tipo',
        'Tipo de Documento',
        required=True
        )
    prefix = fields.Char('Prefijo')
    suffix = fields.Char('Sufijo')
    padding = fields.Integer('Cant. Dígitos Secuencial')
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Secuencia ID',
        help='Secuencia alfanumérica',  # noqa
        ondelete='cascade',
        readonly=True,
        store=True,
        )
    sequence = fields.Integer('Secuencia Inicio', related='sequence_id.number_next_actual', readonly=False, copy=False) #size=5
    active = fields.Boolean(string=_("Activo?"), default=True, tracking=True)

    reparto_id = fields.Many2one(
        'sigmap.reparto',
        ondelete='restrict',
        string='Reparto',
        required=True,
        tracking=True)

    def _get_name_code(self):
        name_sequence = self.tipo_secuencia_id.name.lower().replace(' ','_')
        siglas = self.reparto_id.siglas
        name = _('Secuencia %s - %s') % (name_sequence, siglas)
        code = f'{name_sequence or ""}_{siglas or ""}_code' # _('%s_%s_code') % (name_sequence.lower().replace(' ','_'), siglas)
        return name, code
        
    def _create_sequence(self, vals):
        tipo_secuencia_id = self.env['sigmap.secuencia.tipo'].browse(vals.get('tipo_secuencia_id'))
        name_sequence = tipo_secuencia_id.name
        reparto = self.env['sigmap.reparto'].browse(vals.get('reparto_id'))
        search_code = _('%s_%s_code') % (name_sequence.lower().replace(' ','_'), reparto.siglas)
        company = vals.get('company_id', self.company_id)
        ckeck_sequence = self.env['ir.sequence'].search([('code', '=', search_code),('company_id','=', company.id)], limit=1)
        if ckeck_sequence:
            raise ValidationError(_('Ya existe secuencial para %s en reparto %s') % (name_sequence, reparto.name))
        seq = {
            'name': _('Secuencia %s - %s') % (name_sequence, reparto.siglas),
            'code': search_code,
            'prefix': '', #vals.get('prefix', self.prefix) + '-',
            'suffix': '',
            'padding': vals.get('padding', self.padding),
            'number_next': vals.get('sequence', self.sequence),
            'company_id': company.id,
        }
        return self.env['ir.sequence'].create(seq)
    
    @api.model
    def create(self, vals):
        #self.check_sequence_values()
        vals['sequence_id'] = self.sudo()._create_sequence(vals).id
        return super().create(vals)
        
    def _write_sequence_values(self, vals):
        sequence_values = {}
        # if 'tipo_secuencia_id' in vals:
        #     name_sequence , code_sequence = self._get_name_code()
        #     sequence_values['name'] = name_sequence
        #     sequence_values['code'] = code_sequence
        if 'sequence' in vals:
            sequence_values['number_next'] = vals['sequence']
        if 'padding' in vals:
            sequence_values['padding'] = vals['padding']
        return sequence_values
        
    def write(self, vals):
        sequence_values = self._write_sequence_values(vals)
        self.sequence_id.sudo().write(sequence_values)
        return super(SigmapDocumentoSecuenciaTipo, self).write(vals)
    
    _sql_constraints = [
        ('tipo_servicio_reparto_uniq', 'unique (tipo_secuencia_id,reparto_id)',
            _('La secuencia del tipo de documento para el reparto debe ser única.'))
    ]