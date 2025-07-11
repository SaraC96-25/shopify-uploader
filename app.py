import streamlit as st
import zipfile
import os
import tempfile
import base64
import requests
import mimetypes
import time

# Shopify credentials
SHOPIFY_API_KEY = st.secrets["SHOPIFY_API_KEY"]
SHOPIFY_STORE_URL = st.secrets["SHOPIFY_STORE_URL"]

# UI
st.title("📦 Caricatore Immagini Shopify")

product_id = st.text_input("🔢 Inserisci l'ID del prodotto Shopify")
uploaded_file = st.file_uploader("📁 Carica file .zip con cartelle colorate", type="zip")

if product_id and uploaded_file:
    if st.button("🚀 Carica su Shopify"):

        # Placeholder per progresso
        progress_text = st.empty()
        progress_bar = st.progress(0)

        uploaded_images = 0
        total_images = 0

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "upload.zip")
            with open(zip_path, "wb") as f:
                f.write(uploaded_file.read())

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            # Conta immagini prima di iniziare
            for folder_name in os.listdir(tmpdir):
                folder_path = os.path.join(tmpdir, folder_name)
                if not os.path.isdir(folder_path):
                    continue
                for img_name in os.listdir(folder_path):
                    img_path = os.path.join(folder_path, img_name)
                    if os.path.isfile(img_path):
                        mime_type, _ = mimetypes.guess_type(img_path)
                        if mime_type and mime_type.startswith("image"):
                            total_images += 1

            current_index = 0  # Per la progress bar

            for folder_name in os.listdir(tmpdir):
                folder_path = os.path.join(tmpdir, folder_name)
                if not os.path.isdir(folder_path):
                    continue

                color = folder_name

                for img_name in os.listdir(folder_path):
                    img_path = os.path.join(folder_path, img_name)

                    # Verifica file immagine
                    if not os.path.isfile(img_path):
                        continue
                    mime_type, _ = mimetypes.guess_type(img_path)
                    if not mime_type or not mime_type.startswith("image"):
                        continue

                    # Codifica immagine
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

                    current_index += 1
                    progress = current_index / total_images
                    progress_bar.progress(progress)
                    progress_text.text(f"Caricamento {current_index} di {total_images} immagini...")

                    if response.status_code == 201:
                        st.success(f"✅ '{img_name}' caricata (alt: {color})")
                        uploaded_images += 1
                    elif response.status_code == 422:
                        st.warning(f"⚠️ '{img_name}' già esistente.")
                    else:
                        st.error(f"❌ Errore su '{img_name}': {response.status_code} - {response.text}")

        # 🎵 Suono di completamento (usa HTML per riprodurlo)
        st.markdown("""
            <audio autoplay>
              <source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg">
              Il tuo browser non supporta l'audio HTML5.
            </audio>
        """, unsafe_allow_html=True)

        st.balloons()
        st.success(f"🎉 Caricamento completato: {uploaded_images} immagini caricate.")
