# comandos/telp.py

def manejar_telp(respuesta):
    """
    Procesa la respuesta de /telp para formatearla en una plantilla elegante.

    Args:
        respuesta (str): La respuesta recibida de la consulta.

    Returns:
        str: Respuesta formateada.
    """
    return formatear_respuesta_telp(respuesta)


def formatear_respuesta_telp(respuesta):
    """
    Formatea la respuesta de /telp en una plantilla elegante.

    Args:
        respuesta (str): La respuesta original de la consulta /telp.

    Returns:
        str: La respuesta formateada en una plantilla elegante.
    """
    bloques = respuesta.split("\n\n")
    datos_extraidos = []

    for bloque in bloques:
        datos = {}
        lineas = bloque.split("\n")

        for linea in lineas:
            if "DOCUMENTO" in linea or "DNI" in linea:
                datos["documento"] = linea.split(":", 1)[1].strip()
            elif "PLAN" in linea:
                datos["plan"] = linea.split(":", 1)[1].strip()
            elif "FUENTE" in linea:
                datos["fuente"] = linea.split(":", 1)[1].strip()
            elif "NUMERO" in linea:
                datos["numero"] = linea.split(":", 1)[1].strip()
            elif "FECHA ACTIVACION" in linea or "FECHA DE REGISTRO" in linea:
                datos["fecha_activacion"] = linea.split(":", 1)[1].strip()
            elif "FECHA ACTUALIZACION" in linea or "FECHA DE MODIFICACION" in linea:
                datos["fecha_actualizacion"] = linea.split(":", 1)[1].strip()

        if datos:
            datos_extraidos.append(datos)

    # Plantilla elegante
    plantilla = [
        """\n╔════════════════════════════════╗\n║       📞 RESULTADOS TELP       ║\n╠════════════════════════════════╣"""
    ]

    for idx, datos in enumerate(datos_extraidos, start=1):
        plantilla.append(f"║ 📋 Resultado #{idx:<21}║")
        plantilla.append("╟──────────────────────────────╢")
        plantilla.append(f"║ DOCUMENTO: {datos.get('documento', 'N/A'):<22}║")
        plantilla.append(f"║ PLAN: {datos.get('plan', 'N/A'):<27}║")
        plantilla.append(f"║ FUENTE: {datos.get('fuente', 'N/A'):<25}║")
        plantilla.append(f"║ NUMERO: {datos.get('numero', 'N/A'):<26}║")
        plantilla.append(f"║ FECHA ACTIVACION: {datos.get('fecha_activacion', 'N/A'):<15}║")
        plantilla.append(f"║ FECHA ACTUALIZACION: {datos.get('fecha_actualizacion', 'N/A'):<11}║")
        plantilla.append("╚════════════════════════════════╝\n")

    return "\n".join(plantilla)
