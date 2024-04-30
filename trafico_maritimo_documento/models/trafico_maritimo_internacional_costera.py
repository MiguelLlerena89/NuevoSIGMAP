from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class TraficoMaritimoInternacionalCostera(models.Model):
    _inherit = 'trafico.maritimo.internacional.costera'

    tramite_id = fields.Many2one(
        string='Tramite',
        comodel_name='tramite',
        ondelete='restrict',
        readonly=True,
        store=True,
        index=True,
        tracking=True
    )

    @api.constrains('nave_id','ultimo_evento','tramite_id')
    def _check_nave_ultimo_evento_tramite(self):
        for rec in self:
            domain = [
                ('nave_id','=', rec.nave_id.id),
                #('ultimo_evento','=', rec.ultimo_evento),
                ('tramite_id','=', False),
            ]
            prenavegacion = self.search(domain)
            if len(prenavegacion) > 1:
                raise ValidationError(_('Existe un proceso de pre-navegación vigente'))

    @api.ondelete(at_uninstall=False)
    def _unlink_except_if_tramite_id(self):
        if self.tramite_id:
            raise UserError(_('El %s: %s no puede ser eliminado porque está asociado al tramite %s.')
                            % (self.ultimo_evento_descripcion, self.name, self.tramite_id.name))