from odoo import http
from odoo.http import request
from .utils import Utils

class Reversar(http.Controller):
    operacion = "reversar"
    
    @http.route('/ws/recaudacion/reversar/<string:codigo>', auth='public', type='json')
    def reversar_recaudacion(self, codigo, **params):
        if request.httprequest.method == 'POST':
            return self.process_reversar(codigo,params)
        else:    
            return Utils.get_error_response(self.operacion,"109","HTTP REQUEST METODO NO PERMITIDO")
    
    
    def process_reversar(self, codigo, params):
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
        sale_order = http.request.env['sale.order'].sudo().with_context(db=db).search([('recaudacion_codigo', '=',codigo)], limit=1)
        if not sale_order: return Utils.get_error_response(self.operacion,"103","CODIGO NO EXISTE");

        if sale_order.recaudacion_estado == "RECAUDADO": #002 Indica que esta recaudada por lo tanto se puede reversar
            try:
                #recaudacion.write({'estado': 'NO RECAUDADO', 'recaudado_en': ""}) 
                http.request.env['account.payment'].sudo().with_context(db=db).search([('ref', 'ilike',codigo)], limit=1).unlink()
                sale_order.write({'state' : 'sent','recaudacion_estado': 'NO RECAUDADO'})

                return Utils.get_info_response(self.operacion,"000","TRANSACCION EXITOSA");
            except Exception as e:
                return Utils.get_error_response(self.operacion,"104","TRANSACCION ERROR");

        if sale_order.recaudacion_estado == "NO RECAUDADO":	
            return Utils.get_error_response(self.operacion,"107","EL CODIGO NO SE PUEDE VOLVER A REVERSAR");

        #default codigo 003
        return Utils.get_error_response(self.operacion,"106","EL CODIGO SE ENCUENTRA ANULADO, TIEMPO EXPIRADO");
        
        
        
        
        
        
        
        
        