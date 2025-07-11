import streamlit as st
import zipfile
import os
import tempfile
import base64
import requests
import mimetypes

# Shopify credentials from secrets.toml
SHOPIFY_API_KEY = st.secrets["SHOPIFY_API_KEY"]
SHOPIFY_STORE_URL = st.secrets["SHOPIFY_STORE_URL"]

# UI
st.title("📦 Caricatore Immagini Shopify")

product_id = st.text_input("🔢 Inserisci l'ID del prodotto Shopify")

uploaded_file = st.file_uploader("📁 Carica file .zip con cartelle colorate", type="zip")

if product_id and uploaded_file:
    if st.button("🚀 Carica su Shopify"):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "upload.zip")
            with open(zip_path, "wb") as f:
                f.write(uploaded_file.read())

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            # Loop su tutte le cartelle nel file zip
            for folder_name in os.listdir(tmpdir):
                folder_path = os.path.join(tmpdir, folder_name)
                if not os.path.isdir(folder_path):
                    continue  # Salta se non è una cartella

                color = folder_name  # Nome cartella = colore = alt

                for img_name in os.listdir(folder_path):
                    img_path = os.path.join(folder_path, img_name)

                    # Salta se non è un file immagine
                    if not os.path.isfile(img_path):
                        continue
                    mime_type, _ = mimetypes.guess_type(img_path)
                    if not mime_type or not mime_type.startswith("image"):
                        continue

                    # Leggi immagine e codifica in base64
                    with open(img_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

                    image_data = {
                        "image": {
                            "attachment": encoded_image,
                            "alt": color
                        }
                    }

                    headers = {
                        "Content-Type": "application/json",
                        "X-Shopify-Access-Token": SHOPIFY_API_KEY
                    }

                    api_url = f"{SHOPIFY_STORE_URL}/admin/api/2023-04/products/{product_id}/images.json"

                    response = requests.post(api_url, json=image_data, headers=headers)

                    if response.status_code == 201:
                        st.success(f"✅ Immagine '{img_name}' caricata con alt '{color}'")
                    else:
                        st.error(f"❌ Errore su '{img_name}': {response.text}")
