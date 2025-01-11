# Страница для инференса
import json
import pandas as pd
import streamlit as st
from deployment.frontend.utils.api_client import upload_file, make_prediction, list_models

def show_page():
    st.header("Инференс")
    st.write("Получите предсказания с использованием обученной модели.")

    if "list_model" not in st.session_state:
        st.session_state.list_model = []
    if "model_id" not in st.session_state:
        st.session_state.model_id = None

    if st.button("Обновить список моделей"):
        response = list_models("api/v1/models/list_models")
        if response.status_code == 200:
            st.session_state.list_model = response.json().get("models", [])
            st.success("Список моделей обновлен!")
        else:
            st.error(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")

    if st.session_state.list_model:
        st.session_state.model_id = st.selectbox(
            "Выберите модель для предсказания:",
            st.session_state.list_model,
            index=0 if st.session_state.model_id not in st.session_state.list_model else
            st.session_state.list_model.index(st.session_state.model_id),
            help="Выберите модель, которая будет использоваться для предсказания"
        )
    else:
        st.warning("Список моделей пуст. Сначала обучите модель.")

    st.subheader("Предсказание для одного примера")

    example_data = {}
    columns = ["year", "mileage", "color", "eng_power", "eng_type", "transmission", "drive"]
    for col in columns:
        if col == "year":
            example_data[col] = st.number_input(
                f"{col}:",
                value=0,
                help="Введите год выпуска автомобиля. Например, 2008."
            )
        elif col == "mileage":
            example_data[col] = st.number_input(
                f"{col}:",
                value=0.0,
                help="Введите пробег автомобиля в километрах. Например, 150000."
            )
        elif col == "color":
            example_data[col] = st.selectbox(
                f"{col}:", 
                ["белый", "черный", "серебристый"],
                help="Выберите цвет автомобиля из предложенных вариантов."
            )
        elif col == "eng_power":
            example_data[col] = st.number_input(
                f"{col}:",
                value=0.0,
                help="Введите мощность двигателя в лошадиных силах. Например, 150."
            )
        elif col == "eng_type":
            example_data[col] = st.selectbox(
                f"{col}:", 
                ["Бензин", "Дизель", "Гибрид", "Электро"],
                help="Выберите тип двигателя автомобиля из предложенных вариантов."
            )
        elif col == "transmission":
            example_data[col] = st.selectbox(
                f"{col}:", 
                ["механическая", "автоматическая", "вариатор"],
                help="Выберите тип трансмиссии автомобиля из предложенных вариантов."
            )
        elif col == "drive":
            example_data[col] = st.selectbox(
                f"{col}:", 
                ["передний", "задний", "полный"],
                help="Выберите тип привода автомобиля из предложенных вариантов."
            )

    if st.button("Сделать предсказание (ручной ввод)"):
        if st.session_state.model_id:
            response = make_prediction("api/v1/models/predict", st.session_state.model_id, example_data)
            if response.status_code == 200:
                st.success(f"Предсказание: {response.json()['predictions']}")
            else:
                st.error(f"Ошибка предсказания: {response.json().get('detail', 'неизвестная ошибка')}")
        else:
            st.warning("Выберите модель для предсказания.")

    st.subheader("Предсказание по CSV-файлу")

    uploaded_file = st.file_uploader("Загрузите CSV-файл", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Предварительный просмотр данных:")
            st.dataframe(df.head())

            required_columns = ["year", "mileage", "color", "eng_power", "eng_type", "transmission", "drive"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(f"Отсутствуют необходимые колонки: {', '.join(missing_columns)}")
            else:
                if st.button("Сделать предсказание для CSV"):
                    response = upload_file("api/v1/models/predict_items", uploaded_file)
                    if response.status_code == 200:
                        st.success("Предсказание выполнено успешно!")
                        st.download_button(
                            label="Скачать результаты",
                            data=response.content,
                            file_name="predictions.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(f"Ошибка: {response.json().get('detail', 'неизвестная ошибка')}")
        except Exception as e:
            st.error(f"Ошибка обработки файла: {str(e)}")