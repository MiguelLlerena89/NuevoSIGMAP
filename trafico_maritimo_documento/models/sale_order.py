from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("nave_id")
    def _check_trafico_maritimo_nave(self):
        for rec in self:
            trafico_maritimo_id = self.env.ref("base_sigmap.trafico_maritimo")
            if rec.tipo_documento_id.id == trafico_maritimo_id.id:
                msg = ''
                if rec.nave_id.tipo_trafico_id.tipo == 'INT':
                    evento_selection_values = [key for (key, value) in self.env['trafico.maritimo.internacional.costera'].fields_get(['ultimo_evento'])['ultimo_evento']['selection']]
                    domain = [
                        ('nave_id','=', rec.nave_id.id),
                        ('ultimo_evento','in', evento_selection_values),
                        ('tramite_id', '=', False),
                    ]
                    print(domain)
                    trafico_internacional_id = self.env["trafico.maritimo.internacional.costera"].search(domain, limit=1)
                    if not trafico_internacional_id:
                        msg = 'La nave %s no tiene definido ningún proceso de pre-navegación (Pre-Zarpe ó Pre-Arribo) por Costera' % (rec.nave_id.name)
                        rec.nave_id = None
                        raise ValidationError(_(msg))
                else:
                    if len(rec.nave_id.dotacion_minima_jerarquia_ids) == 0:
                        msg = msg + _('Debe definir la dotación mínima.\n')
                    if len(rec.nave_id.motors_ids) == 0:
                        msg = msg + _('Debe definir los motores.\n')
                    if msg:
                        raise ValidationError(_(msg))
        return True

    @api.onchange("nave_id")
    def _onchange_nave_id(self):
        self._check_trafico_maritimo_nave()

    # @api.constrains("nave_id")
    # def _check_nave_id(self):
    #     self._check_trafico_maritimo_nave()

