from odoo import api, fields, models, _

class AgenciaNavieraPuerto(models.Model):
    _name = 'sigmap.agencia.naviera.puerto'
    _description = _('Agencies and Ports')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # reparto_emision_id
    reparto_id = fields.Many2one(
        'sigmap.reparto',
        ondelete='restrict',
        string=_('Related Distribution'),
        required=True,
        copy=False,
        tracking=True)

    fecha_emision = fields.Date(
        string=_('Issue Date'),
        required=True,
        copy=False,
        tracking=True)

    fecha_caducidad = fields.Date(
        string=_('Expiry Date'),
        required=False,
        copy=False,
        tracking=True)

    agencia_id = fields.Many2one(
        'sigmap.agencia.naviera',
        ondelete='restrict',
        required=True,
        copy=False,
        string=_('Shipping Agency'),
        help=_('Shipping Agency to whom this permission relates'))

    puerto_id = fields.Many2one(
        'sigmap.puerto',
        ondelete='restrict',
        required=True,
        copy=False,
        string=_('Port'),
        help=_('Port to whom this permission relates'))

    # estado [ A | I ]
    active = fields.Boolean(
        string=_('Active?'),
        index=True,
        copy=False,
        tracking=True,
        default=True)


    KEY_STRINGS = {
        'puerto_id': _('Port'),
        'reparto_id': _('Distribution'),
        'fecha_emision': _('Issue Date'),
        'fecha_caducidad': _('Expiry Date')
    }

    def _get_name_from_many2one(self, model_name, rec_id, name_field='name'):
        name = ""
        if model_name and rec_id:
            recs = self.env[model_name].search([('id', '=', rec_id)])
            if recs and len(recs) > 0:
                rec = recs[0]
                name = rec[name_field] if name_field else rec[name]
                name += f" [{rec_id}]"
        return name

    @api.model
    def create(self, vals):

        res = super(AgenciaNavieraPuerto, self).create(vals)

        if res and vals:
            message = _("New") + " " +  _("Port") + ":"
            for k,v in self.KEY_STRINGS.items():
                value = vals[k]
                if 'puerto_id' == k:
                    value = self._get_name_from_many2one('sigmap.puerto', value)
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
            if 'puerto_id' == key:
                value = value.name
            if 'reparto_id' == key:
                value = value.name
            before[key] = value

        res = super().write(vals)

        KEY_STRINGS = dict(
            **self.KEY_STRINGS,
            active=_('Active?')
        )

        if res and vals:
            message = _("Port") + " " + _("updated") + ":"
            if 'puerto_id' not in vals:
                port = self.puerto_id.name
                message += '\n' + _('Port') + f': {port}'
            for k,v in vals.items():
                value = v
                if 'puerto_id' == k:
                    value = self._get_name_from_many2one('sigmap.puerto', value)
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
            message = _("Port") + " " + _("deleted") + ":"
            for k,v in KEY_STRINGS.items():
                value = rec[k]
                if 'puerto_id' == k:
                    value = value.name
                if 'reparto_id' == k:
                    value = value.name
                message += '\n' + v + f': {value}'
            self.agencia_id.message_post(body=message)

        res = super().unlink()

        return res


class AgenciaNaviera(models.Model):
    _inherit = 'sigmap.agencia.naviera'

    agencia_puerto_ids = fields.One2many(
        string=_('Ports'),
        comodel_name='sigmap.agencia.naviera.puerto',
        inverse_name='agencia_id',
        context={'active_test': False})

    puertos_activos = fields.Char(
        compute='_compute_puertos_agencia',
        string=_('Ports'))


    @api.depends('agencia_puerto_ids')
    def _compute_puertos_agencia(self):
        for rec in self:
            rec.puertos_activos = ''

            if rec.agencia_puerto_ids:
                puertos_recs = rec.agencia_puerto_ids
                puertos = [puerto.puerto_id.name for puerto in puertos_recs if puerto['active']]
                if len(puertos) > 0:
                    puertos_names = ", ".join(puertos)
                    rec.puertos_activos = puertos_names
