import streamlit as st
import requests

st.title("Обучение модели")
st.subheader("Выберите параметры для обучения")

API_URL = "http://127.0.0.1:8000/api/v1"

if 'model_id' not in st.session_state:
    st.session_state.model_id = ""

model_type = st.selectbox(
    "Тип модели",
    options=["full", "poly", "ohe"],
    index=0,
    help="Выберите тип модели для обучения"
)

model_id = st.text_input(
    "Идентификатор модели",
    placeholder="Введите уникальный ID для модели",
    value=st.session_state.model_id,  
    help="Используйте уникальный ID для сохранения модели"
)

if model_id != st.session_state.model_id:
    st.session_state.model_id = model_id

alpha = st.slider(
    "Коэффициент регуляризации (alpha)",
    min_value=0.01,
    max_value=10.0,
    step=0.01,
    value=1.0,
    help="Регулирует степень регуляризации модели"
)

if st.button("Обучить модель"):
    if not model_id:
        st.error("Пожалуйста, укажите идентификатор модели.")
    else:
        config = {
            "id": model_id,
            "ml_model_type": model_type,
            "hyperparameters": alpha,
        }

        with st.spinner("Обучение модели, пожалуйста, подождите..."):
            try:
                response = requests.post(f"{API_URL}/models/fit", json={"config": config})
                if response.status_code == 200:
                    st.success(f"Модель '{model_id}' успешно обучена!")
                    result = response.json()
                    st.write(f"Сообщение: {result['message']}")
                else:
                    error_detail = response.json().get("detail", "Неизвестная ошибка.")
                    st.error(f"Ошибка: {error_detail}")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка соединения с сервером: {e}")

st.subheader("Список доступных моделей")

models = []  

if st.button("Обновить список"):
    with st.spinner("Загрузка списка моделей..."):
        try:
            response = requests.get(f"{API_URL}/models/list_models")
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    st.write("Доступные модели:")
                    model_details = [] 
                    for model in models:
                        model_details.append({
                            "id": model.get("id", "Неизвестно"),
                            "date": model.get("date_updated", "Неизвестно"),
                            "status": model.get("status", "Неизвестно"),
                            "accuracy": model.get("accuracy", "Неизвестно"),
                        })
                        st.write(f"- {model.get('id', 'Неизвестно')} (Дата обновления: {model.get('date_updated', 'Неизвестно')}, Статус: {model.get('status', 'Неизвестно')}, Точность: {model.get('accuracy', 'Неизвестно')}%)")
                    
                    st.write("Дополнительная информация о моделях:")
                    st.table(model_details)
                else:
                    st.info("Нет доступных моделей.")
            else:
                error_detail = response.json().get("detail", "Неизвестная ошибка.")
                st.error(f"Ошибка: {error_detail}")
        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка соединения с сервером: {e}")

st.subheader("Кривая обучения")

if models:
    models_to_visualize = st.multiselect(
        "Выберите ID моделей для отображения кривых обучения",
        options=[model["id"] for model in models],
        help="Выберите одну или несколько моделей для отображения кривой обучения"
    )

    if st.button("Показать кривую обучения"):
        if not models_to_visualize:
            st.error("Пожалуйста, выберите хотя бы одну модель.")
        else:
            with st.spinner("Загрузка кривых обучения..."):
                for model_id in models_to_visualize:
                    try:
                        response = requests.post(
                            f"{API_URL}/models/learning_curve",
                            json={"id": model_id}
                        )
                        if response.status_code == 200:
                            learning_curve_data = response.json()
                            st.write(f"Кривая обучения для модели '{model_id}':")
                            chart_data = {
                                "Ошибка на трейне": learning_curve_data["train_errors"],
                                "Ошибка на тесте": learning_curve_data["test_errors"]
                            }
                            st.line_chart(chart_data)
                        else:
                            error_detail = response.json().get("detail", "Неизвестная ошибка.")
                            st.error(f"Ошибка: {error_detail}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Ошибка соединения с сервером: {e}")
else:
    st.warning("Нет доступных моделей для отображения кривой обучения.")

st.subheader("Графики и метрики для обученных моделей")

if models:
    if st.button("Показать дополнительные графики"):
        model_to_analyze = st.selectbox("Выберите модель для анализа", options=[model["id"] for model in models])
        with st.spinner("Загрузка дополнительных метрик..."):
            try:
                response = requests.post(
                    f"{API_URL}/models/evaluation",
                    json={"id": model_to_analyze}
                )
                if response.status_code == 200:
                    eval_data = response.json()
                    
                    st.write(f"Матрица ошибок для модели '{model_to_analyze}':")
                    st.image(eval_data.get('confusion_matrix'), caption="Матрица ошибок")

                    st.write(f"Точность модели: {eval_data.get('accuracy', 'Неизвестно')}%")
                    st.write(f"F1-Score: {eval_data.get('f1_score', 'Неизвестно')}")

                    if 'roc_curve' in eval_data:
                        st.write("ROC-Кривая:")
                        st.image(eval_data.get('roc_curve'), caption="ROC-Кривая")
                else:
                    st.error("Не удалось загрузить метрики для выбранной модели.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка соединения с сервером: {e}")
else:
    st.warning("Нет доступных моделей для анализа.")
