from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied

class TramiteController(http.Controller):

    @http.route(['/apiv1/tramites/'], type="json", auth="user")
    def get_info_personal_maritimo(self, identificacion, **kwargs):
        tramite = request.env['tramite'].sudo().search([
            ('personal_maritimo_id.vat', '=', identificacion),
            ('state', 'in', ['draft']),
            ('servicio_id', '=', request.env.ref('tramite.tramite_documento_88').id)
            ],
            order="create_date desc",
            limit=1)
        if not tramite:
            return {}

        jerarquia = tramite.personal_maritimo_id.jerarquia_id
        if jerarquia:
            jerarquia = tramite.personal_maritimo_id.jerarquia_id.name
        else:
            jerarquia = ""

        reparto = tramite.reparto_id
        responsable_grado = ""
        responsable_nombre = ""
        if reparto:
            reparto_name = tramite.reparto_id.name
            if reparto.responsable_id:
                responsable_nombre = reparto.responsable_id.name
                if reparto.responsable_id.rango_id:
                    responsable_grado = reparto.responsable_id.rango_id.abreviatura + ' '
                if reparto.responsable_id.especialidad_id:
                    responsable_grado += reparto.responsable_id.especialidad_id.abreviatura

        return {
            "persona": tramite.personal_maritimo_id.name,
            "solicitud": tramite.order_id.name,
            "jerarquia": jerarquia,
            "reparto": reparto_name,
            "responsable_nombre": responsable_nombre,
            "responsable_grado": responsable_grado,
        }

    @http.route('/apiv1/authenticate/', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):

        try:
            request.session.authenticate(db, login, password)
        except AccessDenied:
            return {'error': 'Credenciales inválidas'}

        session_info = request.env['ir.http'].session_info()
        uid = session_info['uid']
        name = session_info['name']
        username = session_info['username']

        return {
            'uid': uid,
            'name': name,
            'username': username
            }