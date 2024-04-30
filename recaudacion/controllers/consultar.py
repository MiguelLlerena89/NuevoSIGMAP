from odoo import http
from odoo.http import request
from .utils import Utils

class Consultar(http.Controller):
    operacion = "consultar"
    
    @http.route('/ws/recaudacion/consultar/<string:codigo>', auth='public', type='json')
    def consultar_recaudacion(self, codigo, **params):
        if request.httprequest.method == 'POST':
            return self.process_consultar(codigo,params)
        else:    
            return Utils.get_error_response(self.operacion,"109","HTTP REQUEST METODO NO PERMITIDO")
    
    
    def process_consultar(self, codigo, params):
        user     = params.get('user','')
        password = params.get('password','')
        canal    = params.get('canal','')
        agencia  = params.get('agencia','')
        provincia = params.get('provincia','')

        user_id = Utils.is_ok_login(user,password);
        if not user_id: return Utils.get_error_response(self.operacion,"100","ACCESO NO PERMITO");	
        
        resp = Utils.is_ok_fields(self.operacion,codigo,canal,agencia,provincia);    	
        if resp is not True: return resp

        db = Utils.get_db_recaudacion_env()
        sale_order = http.request.env['sale.order'].sudo().with_context(db=db).search([('recaudacion_codigo','=',codigo)], limit=1)
        if not sale_order: return Utils.get_error_response(self.operacion,"103","CODIGO NO EXISTE");
        
        if sale_order.recaudacion_estado == "NO RECAUDADO":
            return Utils.get_info_response(self.operacion,"001","CODIGO NO RECAUDADO",sale_order);

        if sale_order.recaudacion_estado == "RECAUDADO":	
            return Utils.get_info_response(self.operacion,"002","CODIGO RECAUDADO");

        #default codigo 003
        return Utils.get_info_response(self.operacion,"003","CODIGO ANULADO, TIEMPO EXPIRADO");
        
        
        
        
        
        
        
        
        