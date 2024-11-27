from flask import Flask, request, jsonify
from utils import extract_carnet_data
import boto3
import os
import logging

app = Flask(__name__)

# Configurar el log de Flask para mostrar detalles de errores
app.config['PROPAGATE_EXCEPTIONS'] = True
logging.basicConfig(level=logging.DEBUG)

# Configuración de AWS desde variables de entorno
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "bankames3")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Crear clientes de AWS
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
textract_client = boto3.client(
    'textract',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

@app.route('/process_carnet', methods=['POST'])
def process_carnet():
    # Verificar si las imágenes requeridas están presentes en la solicitud
    if 'anverso' not in request.files or 'reverso' not in request.files or 'selfie' not in request.files:
        return jsonify({"error": "Se requieren las imágenes de 'anverso', 'reverso' y 'selfie'"}), 400

    # Archivos subidos
    files = {
        "anverso": request.files['anverso'],
        "reverso": request.files['reverso'],
        "selfie": request.files['selfie']
    }

    uploaded_files = {}

    # Subir las imágenes al bucket S3
    try:
        for key, file in files.items():
            file_name = f"{key}_{file.filename}"
            s3_client.upload_fileobj(file, BUCKET_NAME, file_name, ExtraArgs={'ACL': 'public-read'})
            uploaded_files[key] = f"s3://{BUCKET_NAME}/{file_name}"  # URL completa del archivo
    except Exception as e:
        return jsonify({"error": f"Error subiendo las imágenes a S3: {str(e)}"}), 500

    # Procesar las imágenes de anverso y reverso con Amazon Textract
    try:
        def analyze_image_s3(file_key):
            response = textract_client.analyze_document(
                Document={"S3Object": {"Bucket": BUCKET_NAME, "Name": file_key}},
                FeatureTypes=["FORMS"]
            )
            return response

        anverso_key = uploaded_files["anverso"].split("/")[-1]
        reverso_key = uploaded_files["reverso"].split("/")[-1]

        anverso_textract = analyze_image_s3(anverso_key)
        reverso_textract = analyze_image_s3(reverso_key)

    except Exception as e:
        return jsonify({"error": f"Error procesando imágenes con Textract: {str(e)}"}), 500

    # Extraer los datos procesados del OCR
    try:
        processed_data = extract_carnet_data(anverso_textract, reverso_textract)
        processed_data["selfie_url"] = uploaded_files["selfie"]  # Agregar la URL de la selfie
        return jsonify(processed_data)
    except Exception as e:
        return jsonify({"error": f"Error procesando los datos del carnet: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
