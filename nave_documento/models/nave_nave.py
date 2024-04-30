from odoo import api, fields, models, _

class NaveListaAutorizada(models.Model):
    _name = "nave.nave.autorizada.documento"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ESTADOS_DOCUMENTO_EMITIDO = {
        'en_tramite': 'En Trámite',
        'por_supervisar': 'Por supervisar',
        'por_firmar': 'Por Aprobar',
        #'vigente': 'Vigente',
        #'utilizado': 'Utilizado',
        'suspendido': 'Suspendido',
        #'por_caducar': 'Por caducar',
        'caducado': 'Caducado',
        'anulado': 'Anulado'
    }

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].sudo().search([])]

    nave_id = fields.Many2one('nave.nave', string='Nave')
    servicio_id = fields.Many2one("tramite.documento", "Servicios", tracking=True)
    documento_ref = fields.Reference(string='Documento', selection='_selection_target_model', compute='_compute_endoso_caducidad')
    fecha_inicio = fields.Date('Emisión', compute='_compute_endoso_caducidad')
    fecha_proximo_endoso = fields.Date('Próximo Endoso', compute='_compute_endoso_caducidad')
    fecha_caducidad = fields.Date('Caducidad', compute='_compute_endoso_caducidad')
    estado = fields.Selection([
        ('en_tramite', 'En Trámite'),
        ('por_supervisar', 'Por supervisar'),
        ('por_firmar', 'Por Aprobar'),
        ('vigente', 'Vigente'),
        ('utilizado', 'Utilizado'),
        ('suspendido', 'Suspendido'),
        ('por_caducar', 'Por caducar'),
        ('caducado', 'Caducado'),
        ('anulado', 'Anulado'),
    ], string='Estado', compute='_compute_endoso_caducidad')
    fecha_endoso_caducidad = fields.Char('Endoso/Caducidad', compute='_compute_endoso_caducidad')

    def _get_str_estado_requisito(self, doc):
        self.ensure_one()
        fecha_caducidad = doc.fecha_caducidad
        if doc.state == "vigente":
            return f"caduca {fecha_caducidad}" if doc.fecha_caducidad else "No caduca"
        elif doc.state == "por_caducar":
            return f"{fecha_caducidad} (No Válido)"
        else:
            return self.ESTADOS_DOCUMENTO_EMITIDO[doc.state]

    @api.depends('servicio_id')
    def _compute_endoso_caducidad(self):
        for requisito in self:
            requisito.fecha_inicio = requisito.fecha_proximo_endoso = requisito.fecha_caducidad = False
            requisito.documento_ref = requisito.estado = requisito.fecha_endoso_caducidad = False

            modelo_requisito = requisito.servicio_id.model_model
            if not modelo_requisito:
                break

            if modelo_requisito:
                nave_id = requisito.nave_id
                servicio_id = requisito.servicio_id
                doc, es_completado = self.env[modelo_requisito].validar_como_requerido(
                    model=modelo_requisito,
                    tipo_documento_id=requisito.servicio_id.tipo_documento_id,
                    personal_maritimo_id=False,
                    curso_id=False,
                    jerarquia_id=False,
                    nave_id=nave_id,
                    servicio_id=servicio_id,
                )
                if doc:
                    if hasattr(doc, '_name') and hasattr(doc, 'id'):
                        requisito.documento_ref = f'{doc._name},{doc.id}'
                    requisito.fecha_inicio = doc.fecha_inicio
                    requisito.fecha_caducidad = doc.fecha_caducidad
                    requisito.fecha_proximo_endoso = False
                    requisito.estado = doc.state
                    requisito.fecha_endoso_caducidad = requisito._get_str_estado_requisito(doc)


class Nave(models.Model):
    _inherit = 'nave.nave'


    lista_autorizada_id = fields.Many2one(
        'nave.lista.autorizada',
        string=_('Lista Autorizada'),
        compute='compute_lista_autorizada')
    lista_autorizada_error_msg = fields.Text(
        string=_('Lista Autorizada (Error Asignación)'),
        compute='compute_lista_autorizada')

    dotacion_minima_id = fields.Many2one(
        'nave.dotacion.minima',
        string=_('Dotacion Mínima'))

    dotacion_minima_jerarquia_ids = fields.One2many(
        related='dotacion_minima_id.jerarquia_ids',
        string=_('Dotación Mínima')
    )

    documento_ids = fields.One2many('nave.nave.autorizada.documento', 'nave_id', string='Certificados')


    def _find_record_reglas_se_cumplen(self, opciones, reglas_field_name):
        self.ensure_one()
        opciones_validas = []
        registro_id = msg_error = False
        for opcion in opciones:
            domain = [regla.get_domain_tuple() for regla in opcion[reglas_field_name]]
            nave_id = self.id if type(self.id) == int else self.id.origin
            domain.append(('id', '=', nave_id))
            if self.env['nave.nave'].search(domain):
                opciones_validas.append(opcion.name)
                registro_id = opcion.id

        if not opciones_validas:
            msg_error = f"ERROR! \nNingún registro tiene reglas que cumplan para esta Nave: {self.name}"
        if len(opciones_validas) > 1:
            msg_error = f"ERROR! \nLas reglas se cumplen para distintos registros con la misma Nave: {self.name}\n  - "
            msg_error += "\n  - ".join(opciones_validas)
            registro_id = False

        return registro_id, msg_error


    FIELDS_FOR_DOMAIN_REGLAS = [
        'eslora',
        'trb',
        'nave_tipo_id',
        'nave_origen_id',
        'nave_servicio_id',
        'nave_zona_id']

    #@api.depends(*FIELDS_FOR_DOMAIN_REGLAS)
    def compute_lista_autorizada(self):
        listas = self.env['nave.lista.autorizada'].search([('regla_ids','!=',False)])
        for rec in self:
            rec.lista_autorizada_id, rec.lista_autorizada_error_msg = rec._find_record_reglas_se_cumplen(listas, 'regla_ids')

            rec._load_reload_documento_ids()

    def find_listas_chequeo_for_service(self, service_id):
        self.ensure_one()
        try:
            listas = self.env['lista.chequeo'].search([('servicio_id','=',service_id)])
            return self._find_record_reglas_se_cumplen(listas, 'regla_ids')
        except Exception as err:
            _logger.exception(f"Error! listas de chequeo no encontradas para nave {self.name}." )
            return False, f"ERROR! \nNingún registro tiene reglas que cumplan para esta Nave: {self.name}"

    def _clean_documento_ids(self):
        self.ensure_one()
        if self.documento_ids:
            delete_docs = [(2, doc.id) for doc in self.documento_ids]
            self.write({'documento_ids': delete_docs})

    def _load_reload_documento_ids(self):
        self.ensure_one()
        self._clean_documento_ids()
        if self.lista_autorizada_id:
            docs = [(0, 0, { 'servicio_id':doc.servicio_id.id }) for doc in self.lista_autorizada_id.documento_ids]
            self.write({'documento_ids': docs})

    def _get_dotacion_minima(self):
        self.ensure_one()
        dotacion_minima = []
        for dotacion in self.dotacion_minima_jerarquia_ids:
            dotacion_minima.append(dict(
                jerarquia_id=dotacion.jerarquia_id.id,
                #jerarquia_name=dotacion.jerarquia_id.name,
                min_number=dotacion.number
            ))
        return dotacion_minima

    def get_tipo_de_inspector(self):
        ext_id = "sigmap_inspector_10_trb"
        self.ensure_one()
        if self.en_fletamento_o_contrato():
            ext_id = "sigmap_inspector_rector"
        elif self.trb > 150:
            ext_id = "sigmap_inspector_mayores"
        elif self.trb > 10:
            ext_id = "sigmap_inspector_menores"

        ext_id = f"usuarios.{ext_id}"
        return self.env.ref(ext_id)
