from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep import helpers
from zeep.transports import Transport
import logging.config

import unicodedata
import re

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})


url = 'https://interoperabilidad.dinardap.gob.ec/interoperador-v2?wsdl'

def _get_conexion():
    session = Session()
    session.auth = HTTPBasicAuth('DiRnEAInTR22', 'gDKj?n1Wx#dYzQ')
    client = False
    try:
        client = Client(url, transport=Transport(session=session, timeout=5, operation_timeout=10))
        print(client)
    except Exception as e:
        print('Error', e)
        return False
    return client

def _get_data_registro_civil(vat):
    session = Session()
    session.auth = HTTPBasicAuth('DiRnEAInTR22', 'gDKj?n1Wx#dYzQ')
    client = False
    try:
        client = Client(url, transport=Transport(session=session, timeout=2, operation_timeout=3))
        print(client)
    except Exception as e:
        print('Error', e)

    parametro = client.get_type('ns0:parametro')
    parametros = client.get_type('ns0:parametros')

    obj = parametro(nombre="codigoPaquete", valor="4997")
    obj2 = parametro(nombre="identificacion", valor=vat)

    result = client.service.consultar(parametros([obj, obj2]))
    if not result:
        return False

    data = {}
    for clave, valores in helpers.serialize_object(result)['entidades'].items():
    #for clave, valores in result['entidades'].items():
        print(clave, valores)
        for valor in valores:
            for valor_fila, fila in valor['filas'].items():
                for columnas in fila:
                    for clave_col, columna in columnas['columnas'].items():
                        for detalle_col in columna:
                            print(detalle_col)
                            if 'fechaDefuncion' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                data.update({
                                    'fechaDefuncion': detalle_col['valor']
                                    })

                            if 'tipoDiscapacidad' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                data.update({
                                    'tipoDiscapacidad': detalle_col['valor']
                                    })

                                if 'porcentajeDiscapacidad' in detalle_col['campo'] and detalle_col['valor'] is not None:
                                    data.update({
                                        'porcentajeDiscapacidad': detalle_col['valor']
                                        })
    return data

def _get_data_sri(vat):

    client = _get_conexion()
    parametro = client.get_type('ns0:parametro')
    parametros = client.get_type('ns0:parametros')

    obj = parametro(nombre="codigoPaquete", valor="4999")
    obj2 = parametro(nombre="identificacion", valor=vat)
    obj3 = parametro(nombre="fuenteDatos", valor='')

    result = client.service.consultar(parametros([obj, obj2, obj3]))
    if not result:
        return False

    data = {}
    for clave, valores in helpers.serialize_object(result)['entidades'].items():
    #for clave, valores in result['entidades'].items():
        print(clave, valores)
    return data

def _get_data_antecedentes_penales(vat):

    client = _get_conexion()

    if client:
        parametro = client.get_type('ns0:parametro')
        parametros = client.get_type('ns0:parametros')

        obj = parametro(nombre="codigoPaquete", valor="5756")
        obj2 = parametro(nombre="identificacion", valor=vat)

        result = client.service.consultar(parametros([obj, obj2]))
        if not result:
            return False

        data = {}
        for clave, valores in helpers.serialize_object(result)['entidades'].items():
        #for clave, valores in result['entidades'].items():
            print(clave, valores)
        return data
    return False

class customStringUtils:

    def normalize_text(text):
        if not text or (type(text) != str):
            return ""
        return re.sub(r'[^a-zA-Z0-9\s]', '', unicodedata.normalize('NFD', text))

    def text_to_code(text):
        if not text or (type(text) != str):
            return ""

        normalized = customStringUtils.normalize_text(text)
        return normalized.lower().replace(" ", "_")
