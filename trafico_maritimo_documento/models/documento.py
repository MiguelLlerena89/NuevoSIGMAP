from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class TramiteDocumento(models.Model):
    _inherit = "tramite.documento"

    tipo_trafico_id = fields.Many2one(
        'tipo.trafico',
        ondelete='restrict',
        string=_('Tipo Tráfico'),
        copy=False,
        tracking=True)
    tipo = fields.Selection(related='tipo_trafico_id.tipo', string='Tipo', store=True)

    ultimo_evento = fields.Selection([
        ('A', 'Arribo'),
        ('Z', 'Zarpe'),
        # ('S', 'Salío de Área Sitrame'),
        # ('P', 'Plan de viaje (previo arribo/zarpe)'),
        # ('F', 'Prearribo'),
    ], string=_('Evento'), store=True, index=True, copy=False, tracking=True)