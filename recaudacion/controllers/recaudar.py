from odoo import http, fields
from odoo.http import request
from .utils import Utils
from odoo import api, SUPERUSER_ID

class Recaudar(http.Controller):
    operacion = "recaudar"

    @http.route('/ws/recaudacion/recaudar/<string:codigo>', auth='public', type='json')
    def recaudar_recaudacion(self, codigo, **params):
        if request.httprequest.method == 'POST':
            return self.process_recaudar(codigo,params)
        else:
            return Utils.get_error_response(self.operacion,"109","HTTP REQUEST METODO NO PERMITIDO")


    def process_recaudar(self, codigo, params):
        user     = params.get('user','')
        password = params.get('password','')
        canal    = params.get('canal','')
        agencia  = params.get('agencia','')
        provincia = params.get('provincia','')
        valorRecaudado = params.get('valorRecaudado','')

        user_id = Utils.is_ok_login(user,password);
        if not user_id: return Utils.get_error_response(self.operacion,"100","ACCESO NO PERMITO");	
        
        resp = Utils.is_ok_fields(self.operacion,codigo,canal,agencia,provincia);    	
        if resp is not True: return resp
        
        resp = Utils.is_ok_valorRecaudado(self.operacion,valorRecaudado);    	
        if resp is not True: return resp

        db = Utils.get_db_recaudacion_env()
        sale_order = http.request.env['sale.order'].sudo().with_context(db=db).search([('recaudacion_codigo', '=',codigo)], limit=1)
        if not sale_order: return Utils.get_error_response(self.operacion,"103","CODIGO NO EXISTE");

        if sale_order.recaudacion_estado == "NO RECAUDADO":
            try:
                #recaudacion.write({'recaudacion_estado': 'RECAUDADO', 'recaudado_en': provincia + "/" + agencia + " [" + canal + "]"})
                
                
                # Crear registro en account.payment
                payment = http.request.env['account.payment'].sudo().create({
                    'partner_id': sale_order.partner_id.id,
                    'amount': valorRecaudado,
                    'payment_type': 'inbound',  # Tipo de pago: entrada
                    'ref': 'Codigo de Recaudación #%s' % sale_order.recaudacion_codigo,
                    'caja_id': 1,
                    'name': "PBNK1/" + str(fields.Date.today().year) + "/" + sale_order.recaudacion_codigo[5:] #TODO: Esto hay que arreglar no debe ser asi!!!
                })

                sale_order.write({'recaudacion_estado': 'RECAUDADO'})
                sale_order.action_confirm()
                
                #http.request.env.cr.execute("UPDATE sale_order SET state = 'recaudado' WHERE id = %s", (recaudacion.sale_order_id.id,)) #TODO: Arreglar esto, no es correcto
                #http.request.env.cr.commit()
                
                return Utils.get_info_response(self.operacion,"000","TRANSACCION EXITOSA");
            except Exception as e:
                return Utils.get_error_response(self.operacion,"104","TRANSACCION ERROR - " + str(e));

        if sale_order.recaudacion_estado == "RECAUDADO":	
            return Utils.get_error_response(self.operacion,"105","EL CODIGO NO SE PUEDE VOLVER A RECAUDAR");

        #default codigo 003
        return Utils.get_error_response(self.operacion,"106","EL CODIGO SE ENCUENTRA ANULADO, TIEMPO EXPIRADO");
        
        
        
        
        
        
        
        
        