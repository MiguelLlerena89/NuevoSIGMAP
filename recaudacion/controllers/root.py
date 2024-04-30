from odoo import http
from odoo.http import request
from .utils import Utils

class Root(http.Controller):
    operacion = "vacia"
    
    @http.route(['/ws','/ws/recaudacion', '/ws/recaudacion/<string:operacion>'], auth='public', type='json')
    def root_recaudacion(self, operacion=None, **params):
        if request.httprequest.method == 'POST':
            return self.process_root(operacion,params)
        else:
            return Utils.get_error_response(self.operacion,"109","HTTP REQUEST METODO NO PERMITIDO")
        
        
    def process_root(self, operacion, params):
        user     = params.get('user','')
        password = params.get('password','')
        
        user_id = Utils.is_ok_login(user,password);
        if not user_id: return Utils.get_error_response("vacia","100","ACCESO NO PERMITO");	
        
        if not operacion or operacion not in ['consultar','recaudar','reversar']:
            return Utils.get_error_response(self.operacion,"108","OPERACION NO EXISTE")
        
        return Utils.get_error_response(self.operacion,"102","FORMATO INCORRECTO. (CODIGO ESTA VACIO)")