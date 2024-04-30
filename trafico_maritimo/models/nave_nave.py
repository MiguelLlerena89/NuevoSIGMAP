from odoo import api, fields, models, _

class Nave(models.Model):
    _inherit = 'nave.nave'

    estado_navegacion = fields.Selection([
        ('en puerto', 'En puerto'),
        ('prezarpe', 'Pre-Zarpe'),
        ('zarpe', 'Zarpado'),
        ('fuera juridiccion', 'Fuera de Juridicción (Salida del País)'),
        ('prearribo', 'Pre-Arribo'),
        ('arribo', 'Arribado'),
    ], string='Estado de Navegación', compute='_get_navegacion', store=True, readonly=True, copy=False, default='en puerto')

    es_nave_nueva_navegacion = fields.Boolean(string=_('Nave Sin Navegación'),
                                    compute='_compute_es_nave_nueva_navegacion',
                                    #store=True, readonly=False, precompute=True,
                                    tracking=True)

    def _compute_es_nave_nueva_navegacion(self):
        for rec in self:
            selection_values = [key for (key, value) in self.env['trafico.maritimo.navegacion'].fields_get(['ultimo_evento'])['ultimo_evento']['selection']]
            print(selection_values)
            domain = [
                ('nave_id','=', rec.id),
                ('ultimo_evento','in', selection_values), #['A','Z']
            ]
            nave_nueva = self.env['trafico.maritimo.navegacion'].search(domain, limit=1)
            #rec.es_nave_nueva_navegacion = bool(nave_nueva)
            rec.es_nave_nueva_navegacion = True if not nave_nueva else False

    @api.depends('es_nave_nueva_navegacion')
    def _get_navegacion(self):
        for nave in self:
            if nave.es_nave_nueva_navegacion:
                nave.estado_navegacion = 'en puerto'
