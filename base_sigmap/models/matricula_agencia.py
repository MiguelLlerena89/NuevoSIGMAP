from odoo import api, fields, models, _

class MatriculaAgencia(models.Model):
    _name = 'sigmap.matricula.agencia'
    _description = _('Relation between the registration number and the Shipping Agency')
    _inherits = {'sigmap.owner.matricula': 'owner_matricula_id'}
    # _inherit = ['mail.thread', 'mail.activity.mixin'] 

    owner_matricula_id = fields.Many2one(
        'sigmap.owner.matricula',
        ondelete='restrict',
        auto_join=True,
        copy=False,
        string=_('Related Registration Number Registry'))
    # overridden inherited fields to bypass access rights, in case you have
    # access to the user but not its corresponding partner

    agencia_id = fields.Many2one(
        'sigmap.agencia.naviera',
        ondelete='restrict',
        required=True,
        copy=False,
        string=_('Shipping Agency'),
        help=_('Shipping Agency to whom the registration number belongs'))

    def _get_agencia_id(self, vals_agencia_id):
        if type(vals_agencia_id) == int:
            return vals_agencia_id
        return vals_agencia_id.origin

    def _deactive_past_matriculas(self, agencia_id):
        matriculas = self.env['sigmap.matricula.agencia'].search([
            ('agencia_id','=',agencia_id),
            ('active','=',True)])
        for matricula in matriculas:
            matricula.write({'active': False})

    def _get_name_from_many2one(self, model_name, rec_id, name_field='name'):
        name = ""
        if model_name and rec_id:
            recs = self.env[model_name].search([('id', '=', rec_id)])
            if recs and len(recs) > 0:
                rec = recs[0]
                name = rec[name_field] if name_field else rec[name]
                name += f" [{rec_id}]"
        return name

    KEY_STRINGS = {
        'codigo_documento': _('Document Code'),
        'numero_formato': _('Format Number'),
        'fecha_emision': _('Issue Date'),
        'fecha_caducidad': _('Expiry Date'),
        'reparto_id': _('Distribution')
    }

    @api.model
    def create(self, vals):
        agencia_id = self._get_agencia_id(vals['agencia_id'])
        self._deactive_past_matriculas(agencia_id)

        res = super(MatriculaAgencia, self).create(vals)

        if res and vals:
            message = _("New registration number:")
            for k,v in self.KEY_STRINGS.items():
                value = vals[k]
                if 'reparto_id' == k:
                    value = self._get_name_from_many2one('sigmap.reparto', value)
                message += '\n' + v + f': {value}'
            res.agencia_id.message_post(body=message)
        
        return res

    @api.model
    def write(self, vals):
        before = dict()
        for key in vals:
            value = self[key]
            if 'reparto_id' == key:
                value = value.name
            before[key] = value

        res = super().write(vals)

        KEY_STRINGS = dict(
            **self.KEY_STRINGS,
            active=_('Active?')
        )

        if res and vals:
            message = _("Registration number updated:")
            code = self.codigo_documento
            message += '\n' + _('Document Code') + f': {code}'
            for k,v in vals.items():
                value = v
                if 'reparto_id' == k:
                    value = self._get_name_from_many2one('sigmap.reparto', value)

                before_code = before[k]
                message += '\n' + KEY_STRINGS[k] + f': {before_code} -> {value}'
            self.agencia_id.message_post(body=message)
        return res

    def unlink(self):
        KEY_STRINGS = dict(
            **self.KEY_STRINGS,
            active=_('Active?')
        )

        for rec in self:
            message = _("Registration number deleted:")
            for k,v in KEY_STRINGS.items():
                value = rec[k]
                if 'reparto_id' == k:
                    value = value.name
                message += '\n' + v + f': {value}'
            self.agencia_id.message_post(body=message)

        res = super().unlink()

        return res
