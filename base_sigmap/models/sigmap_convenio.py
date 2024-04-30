from odoo import api, fields, models, _


class Convenio(models.Model):
    _name = 'sigmap.convenio'
    _description = _('Convenio')
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string=_('Convenio'),
        required=True,
        index=True,
        tracking=True)

    descripcion = fields.Char(
        string=_('descripcion'),
        required=True,
        tracking=True)

    periodo_id = fields.Many2one(
        'sigmap.periodo',
        string=_('Periodo'),
        required=True,
        index=True,
        tracking=True)

    active = fields.Boolean(
        string=_("Activo?"),
        required=True,
        default=True,
        tracking=True)

    capitulo_ids = fields.One2many(
        'sigmap.convenio.capitulo',
        'convenio_id',
        string=_('Capítulos'))

    def write(self, vals):
        res = super().write(vals)
        if res and ('active' in vals) and (not vals['active']):
            for cap in res.capitulo_ids:
                for regl in cap:
                    regl.write({'active': False})
                cap.write({'active': False})
        return res


class ConvenioCap(models.Model):
    _name = 'sigmap.convenio.capitulo'
    _description = _('Convenio - Capítulo')

    convenio_id = fields.Many2one(
        'sigmap.convenio',
        string=_('convenio'),
        required=True)

    name = fields.Char(
        string=_('Capítulo'))
    
    description = fields.Char(
        string=_('Nombre Completo'))

    active = fields.Boolean(
        string=_("Activo?"),
        required=True,
        default=True,
        tracking=True)
    
    regla_ids = fields.One2many(
        'sigmap.convenio.capitulo.regla',
        'capitulo_id',
        string=_('Reglas'))

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.convenio_id:
                name = '%s: %s' % (rec.convenio_id.name, name)
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args = ['|',('name', operator, name),('convenio_id.name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)


class ConvenioCapRegla(models.Model):
    _name = 'sigmap.convenio.capitulo.regla'
    _description = _('Convenio - Capítulo - Regla')

    capitulo_id = fields.Many2one(
        'sigmap.convenio.capitulo',
        string=_('Capítulo'))

    name = fields.Char(
        string=_('Regla'))
    
    description = fields.Html(
        string=_('Descripción'))

    active = fields.Boolean(
        string=_("Activo?"),
        required=True,
        default=True,
        tracking=True)


    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.capitulo_id:
                name = '%s R. %s' % (rec.capitulo_id.name, name)
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            args = ['|',('name', operator, name),'|',('capitulo_id.name', operator, name),('capitulo_id.convenio_id.name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
