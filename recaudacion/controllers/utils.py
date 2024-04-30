from odoo.http import request
import json
import re
import os

class Utils:
    @staticmethod
    def is_ok_login(user, password):
        try:
            db = Utils.get_db_recaudacion_env()
            return request.env['res.users'].sudo().with_context(db=db).authenticate(db, user, password, {})
        except Exception as e:
            return None
	
    @staticmethod
    def get_db_recaudacion_env():
        dbname = os.environ.get('RECAUDACION_DB','sigmap')
        print(dbname)
        return dbname
        #return "migracion" #TODO: Establecer como variable de entorno
        
    @staticmethod    
    def get_error_response(operacion, code, msg):
        return {
            "tipoRespuesta": "ERROR",
            "deOperacion": operacion,
            "codigoRespuesta": code,
            "mensajeRespuesta": msg,
        }
    
    @staticmethod
    def get_error_response_json(operacion, code, msg):
        error = json.dumps(Utils.get_error_response(operacion, code, msg)) 
        
        #response_headers = [('Content-Type', 'application/json')]
        #return json.dumps(error,indent=2), 200, response_headers
        return json.dumps(error)
    
    @staticmethod  
    def get_info_response(operacion, code, msg, sale_order = None):
        info = {
            "tipoRespuesta": "INFO",
            "deOperacion": operacion,
            "codigoRespuesta": code,
            "mensajeRespuesta": msg,
        }
        
        if sale_order:            
            info['recaudacion'] = {
                "codigo": sale_order.recaudacion_codigo,
                "descripcion": "SOLICITUD DE TRAMITES " + sale_order.name,
                "estadoRecaudacion": sale_order.recaudacion_estado,
                "estadoRecaudacionCode": Utils.get_codigo_estado_recaudacion(sale_order.recaudacion_estado),
                "identificacion": sale_order.partner_id.vat,
                "nombreCliente": sale_order.partner_id.name,
                "tipoIdentificacion": Utils.get_codigo_tipo_identificacion(sale_order.partner_id.l10n_latam_identification_type_id.id),
                "valor": str(sale_order.amount_total),
                "codigoEntidad" : "01"
            }       
            
        return info
    
    @staticmethod
    def get_info_response_json(operacion, code, msg, sale_order = None):
        info = Utils.get_info_response(operacion, code, msg, sale_order)
        #response_headers = [('Content-Type', 'application/json')]
        #return json.dumps(info,indent=2), 200, response_headers
        return json.dumps(info)
        
    
    @staticmethod        
    def is_ok_fields(operacion, codigo, canal, agencia, provincia):
        codigo = codigo.strip()
        canal = canal.strip()
        agencia = agencia.strip()
        provincia = provincia.strip()

        if not codigo:
            return Utils.get_error_response(operacion,"102","FORMATO INCORRECTO. (CODIGO ESTA VACIO)")

        if not re.match("[0-9]+",codigo):
            return Utils.get_error_response(operacion,"102","FORMATO INCORRECTO. (CODIGO [" + codigo + "] NO ES NUMERICO)")

        if not canal:
            return Utils.get_error_response(operacion,"102","FORMATO INCORRECTO. (CANAL ESTA VACIO)")

        if not agencia:
            return Utils.get_error_response(operacion,"102","FORMATO INCORRECTO. (AGENCIA ESTA VACIO)")

        if not provincia:
            return Utils.get_error_response(operacion,"102","FORMATO INCORRECTO. (PROVINCIA ESTA VACIO)")

        return True;    
    
    @staticmethod        
    def is_ok_valorRecaudado(operacion, valor):
        valor = str(valor).strip()
        
        if not valor:
            return Utils.get_error_response(operacion,"102","FORMATO INCORRECTO. (VALOR RECAUDADO ESTA VACIO)")

        patron = re.compile(r'^\d+\.?\d{0,2}$')     
        if not bool(patron.match(valor)):
            return Utils.get_error_response(operacion,"102","FORMATO INCORRECTO. (VALOR RECAUDADO [" + valor + "] NO ES DECIMAL)")
        
        return True;
    
    @staticmethod
    def get_codigo_estado_recaudacion(r):
        estados = {
            "RECAUDADO": "002",
            "NO RECAUDADO": "001",
            "ANULADO": "003",
        }
       
        return estados[r]
        
    @staticmethod    
    def get_codigo_tipo_identificacion(i):
        tipos = {
            2: "PAS",
            4: "RUC",
            5: "CED",
            1: "EST"
        }

        return tipos[i]