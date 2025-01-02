# Клиент для взаимодействия с FastAPI
import streamlit as st
import requests


@st.cache_data
def upload_file(endpoint, file=None):
    url = f"http://localhost:8000/{endpoint}"
    files = {'file': (file.name, file.getvalue(), 'text/csv')}
    try:
        resp = requests.post(url, files=files)
        return resp.json()
    except Exception as e:
        st.error(f"Ошибка при отправке файла через API: {e}")
        return None

def preprocess_data(endpoint):
    url = f"http://localhost:8000/{endpoint}"
    try:
        resp = requests.post(url)
        return resp.json()
    except Exception as e:
        st.error(f"Ошибка предобработки датасета через API: {e}")
        return None