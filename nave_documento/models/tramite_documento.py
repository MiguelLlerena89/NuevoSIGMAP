from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

import logging

_logger = logging.getLogger(__name__)

class TramiteDocumento(models.Model):
    _inherit = "tramite.documento"

    es_texto_html = fields.Boolean(string='Adicionar Título y Texto HMTL', index=True, copy=False, tracking=True)

    plantilla_texto = fields.Html(string=_('Plantilla'), copy=False, tracking=True,
        help=_(
            'Puede utilizar las palabras clave:\n' + \
            '  - %%ciudad-fecha%%: GUAYAQUIL, 01 de Enero del 2024\n' + \
            '  - %%reparto%%: CAPITANÍA MAYOR DE GUAYAQUIL\n' + \
            '  - %%nombre-matricula%%: NAVECU 593, con número de matrícula P-00-00001\n' + \
            '  - %%propietario-cedula%%: los sres. Juan Pérez con número de cédula 120XXXXXX2 y Carlos García con número de cédula 092XXXXXX7; Son propietarios\n' + \
            '  - %%bandera%%: Perú\n' + \
            '  - %%numero-registro%%: No. 001-2024\n'
        ))


class Nave(models.Model):
    _inherit = 'nave.nave'


    def get_ciudad_fecha_para_plantilla(self, fecha_datetime=None):
        fecha = fecha_datetime or datetime.now()
        MES = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre"
        }
        ciudad = self.reparto_id.city_id.name
        return "{}, {:02d} de {} del {}".format(ciudad, fecha.day, fecha.month, fecha.year)


    def get_propietarios_para_plantilla(self):
        propietarios = [nave_owner.propietario_id.partner_id for nave_owner in self.nave_propietario_ids]
        base_str = "{} con número de {} {}"
        base_company_str = "la empresa con razón social {} y número de {} {}, es propietaria"

        if len(propietarios) == 0:
            return "las personas no registradas, son propietarios de"
        elif len(propietarios) == 1:
            owner = propietarios[0]
            if owner.company_type == "company":
                return base_company_str.format(owner.name, owner.l10n_latam_identification_type_id.name, owner.vat)
            elif owner.genero == 'F':
                return "la sra. " + base_str.format(owner.name, owner.l10n_latam_identification_type_id.name, owner.vat) + ", es propietaria"
            else:
                return "el sr. " + base_str.format(owner.name, owner.l10n_latam_identification_type_id.name, owner.vat) + ", es propietario"
        else:
            companies = len([p for p in propietarios if p.company_type == 'company'])
            persons = len([p for p in propietarios if p.company_type == 'person'])
            lista_propietarios = [base_str.format(p.name, p.l10n_latam_identification_type_id.name, p.vat) for p in propietarios]
            lista_propietarios_str = ', '.join(lista_propietarios[:-1:])
            lista_propietarios_str += ' y ' + lista_propietarios[-1]
            if companies == 0 and len([p for p in propietarios if p.genero == 'M']) == 1:
                return "los sres. " + lista_propietarios_str + "; Son propietarios"
            elif companies == 0 and len([p for p in propietarios if p.genero in ['M', 'O']]) == 0:
                return "los sras. " + lista_propietarios_str + "; Son propietarias"
            elif persons == 0:
                return "las empresas " + lista_propietarios_str + "; Son propietarias"
            else:
                return "los personas naturales y jurídicas " + lista_propietarios_str + "; Son propietarias"


    def llenar_plantilla(self, plantilla_texto):
        plantilla_llena = plantilla_texto.replace("%%ciudad-fecha%%", self.get_ciudad_fecha_para_plantilla())
        #for key, value in TEXTO_PLANTILLAS.items():
        #    placeholder = "%%{}%%".format(key)
        plantilla_llena = plantilla_llena.replace("%%reparto%%", self.reparto_id.name if self.reparto_id else '')
        plantilla_llena = plantilla_llena.replace("%%propietario-cedula%%", self.get_propietarios_para_plantilla())
        plantilla_llena = plantilla_llena.replace("%%nombre-matricula%%", "{}, con número de matrícula {}".format(self.name, self.matricula or ''))
        plantilla_llena = plantilla_llena.replace("%%bandera%%", self.bandera_pais_id.name if self.bandera_pais_id else '')

        return plantilla_llena
