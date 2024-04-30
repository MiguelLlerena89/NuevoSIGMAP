from odoo import models


class Users(models.Model):
    _inherit = 'res.users'

    def _compute_state(self):
        for user in self:
            if user.id == self.env.ref('tramite_portal.user_tramite_portal').id:
                user.state = 'new'
            else:
                super()._compute_state()
