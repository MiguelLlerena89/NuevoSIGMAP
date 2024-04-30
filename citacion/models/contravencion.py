from odoo import api, fields, models, _

class ContravencionLeyArt(models.Model):
    _name = 'citacion.contravencion.ley.art'
    _description = _('Contravention Law')

    name = fields.Char(
        string=_('Short Name'))
    
    description = fields.Char(
        string=_('Full Description'))


class ContravencionLeyNum(models.Model):
    _name = 'citacion.contravencion.ley.num'
    _description = _('Contravention Law')

    articulo_id = fields.Many2one(
        'citacion.contravencion.ley.art',
        string=_('Article'))

    name = fields.Char(
        string=_('Short Name'))
    
    description = fields.Char(
        string=_('Full Description'))


    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.articulo_id:
                name = '%s N. %s' % (rec.articulo_id.name, name)
            result.append((rec.id, name))
        return result
