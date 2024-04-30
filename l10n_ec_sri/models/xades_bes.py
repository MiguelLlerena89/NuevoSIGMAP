# https://portal.etsi.org/webapp/workprogram/Report_WorkItem.asp?WKI_ID=21353

from lxml import etree
from cryptography.hazmat.primitives.serialization import pkcs12
import xmlsig
from xades import XAdESContext, template, utils, ns
from xades.policy import ImpliedPolicy
from datetime import datetime
import base64
from random import randrange

def create_signature(company, xml):


    def new_range():
        return randrange(100000, 999999)


    # NS e identificadores para referenciaas, etc fueron tomados de comprobante
    # firmado con software oficial "SRI y yo"
    #signature_id = utils.get_unique_id().replace('id-', 'xmldsig-')
    signature_id = f"Signature{new_range()}"
    signature_property_id = f"{signature_id}-SignedPropertiesID{new_range()}"
    certificate_id = f"Certificate{new_range()}"
    reference_uri = f"Reference-ID-{new_range()}"
    signature = xmlsig.template.create(
        xmlsig.constants.TransformInclC14N,
        xmlsig.constants.TransformRsaSha1,
        signature_id,
    )
    xmlsig.template.add_reference(
        signature,
        xmlsig.constants.TransformSha1,
        name=f"SignedPropertiesID{new_range()}",
        uri=f"#{signature_property_id}",
        uri_type="http://uri.etsi.org/01903#SignedProperties",
    )
    xmlsig.template.add_reference(signature, xmlsig.constants.TransformSha1, uri=f"#{certificate_id}")
    ref = xmlsig.template.add_reference(
        signature, xmlsig.constants.TransformSha1, name=reference_uri, uri="#comprobante"
    )

    xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)

    ki = xmlsig.template.ensure_key_info(signature, name=certificate_id)
    data = xmlsig.template.add_x509_data(ki)
    xmlsig.template.x509_data_add_certificate(data)
    xmlsig.template.add_key_value(ki)

    qualifying = template.create_qualifying_properties(signature, name=signature_id)
    utils.ensure_id(qualifying)

    props = template.create_signed_properties(qualifying, name=signature_property_id)
    #props = template.create_signed_properties(qualifying, datetime=datetime.now(), name=f'{signature_id}-signedprops')
    signed_do = template.ensure_signed_data_object_properties(props)

    template.add_data_object_format(
        signed_do,
        f"#{signature_id}-ref0",
        description="FIRMA DIGITAL SRI",
        mime_type="text/xml",
        encoding="UTF-8",
    )

    return signature


def sign(xml, certs):
    ctx = XAdESContext(ImpliedPolicy(xmlsig.constants.TransformSha1))

    ctx.load_pkcs12(certs)
    ctx.sign(xml)
    #verify
    ctx.verify(xml)

    # Remove policy identifier, as SRI uses BES instead of EPES
    #signature_policy_identifier = xml.find('.//xades:SignaturePolicyIdentifier', namespaces=dict(xades=ns.EtsiNS))
    #signature_policy_identifier.getparent()
    #signature_policy_identifier.getparent().remove(signature_policy_identifier)


def sri_xades_bes(comprobante, company):
    xml = etree.fromstring(comprobante.encode('utf-8'))
    signature = create_signature(company, xml)
    xml.append(signature)
    #private_key, certificado principal y adicionales
    certs = pkcs12.load_key_and_certificates(base64.decodebytes(company.certificate),
                                             company.certificate_password.encode())
    sign(signature, certs)

    return etree.tostring(xml).decode('utf-8')
