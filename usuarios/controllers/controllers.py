# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers import home as web_home


class Home(web_home.Home):
    @http.route()
    def web_client(self, s_action=None, **kw):
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)

            if user.reparto_id.forzar_totp and not user.totp_enabled:
                return request.redirect('/my/security')

        return super().web_client(s_action, **kw)
