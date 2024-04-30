from odoo import models, fields, api, _


class Reparto(models.Model):
    _name = 'sigmap.reparto'
    _inherit = ['sigmap.reparto', 'mail.thread', 'mail.activity.mixin']
    _description = 'Reparto'
    _parent_store = True
    _rec_name = 'complete_name'
    _order = 'complete_name'

    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    user_ids = fields.One2many('res.users', 'reparto_id', _('Personal'))

    parent_id = fields.Many2one('sigmap.reparto', 'Reparto superior', index=True,
                                ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_id = fields.One2many('sigmap.reparto', 'parent_id', _('Repartos inferiores'))

    forzar_totp = fields.Boolean('Forzar autenticación en dos pasos', default=False)

    company_id = fields.Many2one('res.company', string='Institución')
    city_id = fields.Many2one('res.city', string='Cantón/Ciudad')
    direccion = fields.Char('Dirección')
    latitud = fields.Float(string='Latitud', digits=(10, 7))
    longitud = fields.Float(string='Longitud', digits=(10, 7))

    # Revisar listado de establecimientos de la compañía
    sri_establecimiento_id = fields.Many2one("l10n_ec.sri.establecimiento")
    establecimiento = fields.Char(related='sri_establecimiento_id.code')

    latitud_dms = fields.Char(string='Latitud DMS', compute='_compute_coordenadas')
    longitud_dms = fields.Char(string='Longitud DMS', compute='_compute_coordenadas')

    responsable_id = fields.Many2one('res.users', string='Responsable')
    #codigo_matricula = fields.Char(string='Matrícula', size=2, tracking=True)

    secuencia_ids = fields.One2many('sigmap.documento.secuencia.tipo', 'reparto_id', _('Personal'))

    @api.depends('name', 'siglas', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for reparto in self:
            if reparto.parent_id:
                reparto.complete_name = f'{reparto.parent_id.complete_name} / {reparto.siglas}' #f'{reparto.parent_id.complete_name} / {reparto.name}'
            else:
                reparto.complete_name = reparto.siglas

    @api.depends('latitud', 'longitud')
    def _compute_coordenadas(self):
        def decdeg2dms(dd, direction='x'):
            try:
                dd = float(dd)
            except ValueError:
                return None

            if dd < 0:
                appendix = 'W' if direction == 'x' else 'S'
            else:
                appendix = 'E' if direction == 'x' else 'N'
            is_positive = dd >= 0
            dd = abs(dd)
            minutes, seconds = divmod(dd * 3600, 60)
            degrees, minutes = divmod(minutes, 60)
            degrees = degrees if is_positive else -degrees
            return (round(degrees, 2), round(minutes, 2), round(seconds, 2), appendix)

        for reparto in self:
            if not reparto.latitud:
                reparto.latitud_dms = ''
            else:
                lat = decdeg2dms(reparto.latitud)
                if not lat:
                    reparto.latitud_dms = ''
                else:
                    reparto.latitud_dms = f"{lat[0]}° {lat[1]}' {lat[2]}'' {lat[3]}"

            if not reparto.longitud:
                reparto.longitud_dms = ''
            else:
                lon = decdeg2dms(reparto.longitud)
                if not lon:
                    reparto.longitud_dms = ''
                else:
                    reparto.longitud_dms = f"{lon[0]}° {lon[1]}' {lon[2]}'' {lat[3]}"

# class SigmapDocumentoSecuenciaTipo(models.Model):
#     _inherit = "sigmap.documento.secuencia.tipo"

#     reparto_id = fields.Many2one(
#         comodel_name='sigmap.reparto',
#         string='Reparto')