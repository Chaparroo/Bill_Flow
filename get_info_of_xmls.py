# Interacción con archivos xml
import xml.etree.ElementTree as ET

# Manipulación de datos
import pandas as pd 

# Manejo de rutas
import os
from pathlib import Path

# prefijos
namespaces = {
    # Necesarios
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ns': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',

    # No necesarios
    "ext":'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    "sts": "dian:gov:co:facturaelectronica:Structures-2-1",
    "xades": "http://uri.etsi.org/01903/v1.3.2#",
    "xades141": "http://uri.etsi.org/01903/v1.4.1#",
    "fn": "http://www.w3.org/2005/xpath-functions",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance" ,
    "ds": "http://www.w3.org/2000/09/xmldsig#",
}

def address_and_files():
    """
    Obtiene la ruta del directorio padre del script actual y una lista de archivos XML en el subdirectorio 'bills_supermarket'.

    La función no recibe parámetros. Primero, determina la ruta absoluta del directorio donde se encuentra el script en ejecución. Luego, accede al subdirectorio 'bills_supermarket' dentro de este directorio padre. Finalmente, lista todos los archivos XML encontrados en este subdirectorio.

    Returns:
        tuple: Un par donde el primer elemento es la ruta del directorio padre del script y el segundo es una lista de nombres de archivos XML encontrados en el subdirectorio 'bills_supermarket'.
    """
    address_script = Path(__file__).resolve()
    parent_path = address_script.parent

    path_bills_supermarket= parent_path / "bills_supermarket" 

    files = os.listdir(path_bills_supermarket)

    xml_files = [file for file in files if file.endswith('.xml')]

    return path_bills_supermarket,xml_files

def process_file(root):
    """
    Procesa un elemento XML raíz para extraer información de líneas de factura y genera un DataFrame.

    Esta función busca dentro del elemento raíz XML proporcionado para encontrar y procesar cada línea de factura ('cac:InvoiceLine'), extrayendo datos como el ID del producto, descripción, precio unitario, cantidad, total por producto, fecha de facturación y cantidad real facturada. Los datos extraídos se agregan a un DataFrame de pandas.

    Parameters:
        root (ElementTree.Element): El elemento raíz del documento XML desde donde se inicia la búsqueda de datos de factura.

    Returns:
        pandas.DataFrame: Un DataFrame que contiene las columnas ["Numero_producto", "Descripcion_producto", "Cantidad_producto", "Precio_producto", "Total_producto", "Fecha_factura", "Cantidad_factura"] con los datos extraídos de cada línea de factura encontrada en el documento XML.

    Raises:
        Exception: Captura y muestra excepciones relacionadas con la búsqueda y extracción de datos dentro del documento XML, sin detener la ejecución de la función.
    """
    df=pd.DataFrame(columns=["Numero_producto","Descripcion_producto","Cantidad_producto","Precio_producto","Total_producto","Fecha_factura","Cantidad_factura"])

    # Busca todos los elementos 'cac:InvoiceLine' que son los productos 
    invoice_lines = root.findall('.//cac:InvoiceLine', namespaces)

    for line in invoice_lines:
        try:

            id_element = line.find('.//cbc:ID', namespaces).text
            description_element= line.find('.//cbc:Description', namespaces).text

            individual_price= float(line.find('.//cbc:PriceAmount', namespaces).text)
            quantity = float(line.find('.//cbc:BaseQuantity', namespaces).text)
            total_produc = float(line.find('.//cbc:LineExtensionAmount', namespaces).text)

            date_generation_element = root.find(".//ns:campoString[@name='FechaGeneracion']", namespaces).text
            real_quantity = (str(root.find(".//ECB14").text).strip())

            df.loc[len(df)]=[id_element,description_element,individual_price,quantity,total_produc,date_generation_element,real_quantity]

        except Exception as e:print(f"Error:{e}")

    return df

def main():
    """
    Procesa múltiples archivos XML de facturación, extrayendo datos específicos y consolidándolos en un único archivo Excel.

    Esta función busca primero la ubicación del script actual y determina el directorio de archivos XML a procesar. Luego, para cada archivo XML en el directorio especificado, parsea el archivo para extraer información de facturación utilizando la función `process_file`, agregando cada DataFrame resultante a una lista. Finalmente, concatena todos los DataFrames en uno solo y lo guarda en un archivo Excel en el mismo directorio.

    No se requieren parámetros de entrada, ya que la función determina automáticamente la ruta del directorio y los archivos a procesar basándose en la ubicación del script ejecutado.

    Efectos secundarios:
        - Genera un archivo Excel (`info_com_xml.xlsx`) en el directorio padre del script, conteniendo la información consolidada de todos los archivos XML procesados.
    """
    parent_path,xml_files=address_and_files()

    dfs_list=[]
    
    # Por cada archivo xml se realiza el siguiente proceso
    for file in xml_files:

        tree = ET.parse(os.path.join(parent_path,file))
        root = tree.getroot()

        df=process_file(root)

        dfs_list.append(df)

    df_result_files = pd.concat(dfs_list, ignore_index=True)

    df_result_files.to_excel(os.path.join(parent_path,"info_xmls.xlsx"),index=False)

if __name__ == "__main__":
    main()
