def extract_carnet_data(anverso_json, reverso_json):
    anverso_data = anverso_json
    reverso_data = reverso_json

    anverso_fields = {
        "numero_carnet": "",
        "valido_hasta": "",
        "serie": "",
        "seccion": ""
    }

    blocks = anverso_data["Blocks"]
    for i, block in enumerate(blocks):
        if block["BlockType"] == "LINE":
            text = block["Text"]
            # Buscar número de carnet
            if "No" in text:
                parts = text.split(" ")
                if len(parts) > 1:
                    anverso_fields["numero_carnet"] = parts[1]
            # Buscar fecha de validez
            elif "Valida hasta el" in text or "Válida hasta el" in text:
                if i + 1 < len(blocks):
                    next_block = blocks[i + 1]
                    if next_block.get("BlockType") == "LINE":
                        anverso_fields["valido_hasta"] = next_block.get("Text", "").strip()
            # Buscar serie
            elif "serie" in text.lower():
                anverso_fields["serie"] = blocks[i+1]["Text"] if i+1 < len(blocks) else ""
            # Buscar sección
            elif "sección" in text.lower():
                anverso_fields["seccion"] = blocks[i+1]["Text"] if i+1 < len(blocks) else ""

    reverso_fields = {
        "nombre_completo": "",
        "fecha_nacimiento": "",
        "estado_civil": "",
        "profesion_ocupacion": "",
        "domicilio": ""
    }

    profession_variants = ["Profesión/Ocupación", "Profesion/Ocupacion", "Profesion/Ocupación", "Profesión/Ocupacion"]

    blocks = reverso_data["Blocks"]
    for i, block in enumerate(blocks):
        if block["BlockType"] == "LINE":
            text = block["Text"]
            # Buscar nombre completo
            if text.startswith("A:"):
                for j in range(i + 1, len(blocks)):
                    next_block = blocks[j]
                    if next_block.get("BlockType") == "LINE":
                        next_text = next_block.get("Text", "").strip()
                        if next_text.isupper() and len(next_text.split()) > 1:
                            reverso_fields["nombre_completo"] = next_text
                            break
            # Buscar fecha de nacimiento
            elif "Nacido el" in text:
                parts = text.split("el")
                if len(parts) > 1:
                    reverso_fields["fecha_nacimiento"] = parts[1].strip()
            # Buscar estado civil
            elif "Estado Civil" in text:
                parts = text.split("Civil")
                if len(parts) > 1:
                    reverso_fields["estado_civil"] = parts[1].strip()
            # Buscar profesión/ocupación
            elif any(variant in text for variant in profession_variants):
                parts = text.split("Ocupación")
                if len(parts) > 1:
                    reverso_fields["profesion_ocupacion"] = parts[1].strip()
            # Buscar domicilio
            elif "Domicilio" in text:
                parts = text.split("Domicilio")
                if len(parts) > 1:
                    reverso_fields["domicilio"] = parts[1].strip()

    # Combinar resultados
    return {
        "anverso": anverso_fields,
        "reverso": reverso_fields
    }
