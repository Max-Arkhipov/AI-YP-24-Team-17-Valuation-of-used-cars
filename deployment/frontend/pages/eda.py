# Страница анализа данных
# импортируем библиотеки
# to run: python -m streamlit run deployment/frontend/pages/eda.py
import plotly.graph_objs as go
import pandas as pd
from deployment.frontend.utils.api_client import *

st.title('Исследовательский анализ данных')
st.subheader('Загрузка файла')
uploaded_file = st.file_uploader("Выберите файл csv", type="csv")
st.markdown('''Загрузите файл csv с данными об автомобилях.  
В файле должны содержаться следующие поля:
- `url_car`	- Ссылка на объявление,
- `car_make` - Марка автомобиля,
- `car_model` - Модель автомобиля,
- `car_gen`	- Поколение,
- `car_type` - 	Кузов,
- `car_compl` - Комплектация,
- `ann_date` - Дата объявления,
- `ann_id` - Уникальный номер объявления,
- `car_price` - Цена автомобиля,
- `ann_city` - Город,
- `link_cpl` - Ссылка на комплектацию,
- `avail` - Наличие,
- `year` - Год выпуска автомобиля,
- `mileage` - Пробег автомобиля,
- `color` - Цвет автомобиля,
- `eng_size` - Объем двигателя (л),
- `eng_power` - Мощность двигателя (л.с.),
- `eng_power_kw` - Мощность электроавтомобиля (кВт),
- `eng_type` - Тип двигателя,
- `pow_resrv` - Запас хода (км),
- `options`	- Опции,
- `transmission` - Трансмиссия,
- `drive` - Привод,
- `st_wheel` - Расположение руля,
- `condition` - Состояние,
- `count_owner`	- Число владельцев,
- `original_pts` - Оригинал ПТС,
- `customs`	- Растоможен,
- `url_compl` - Ссылка на страницу с комплектацией,
- `state_mark` - Страна марки,
- `class_auto` - Класс автомобиля,
- `door_count` - Количество дверей,
- `seat_count` - Количество мест
- `long` - Длина (мм),
- `width` - Ширина (мм),
- `height` - Высота (мм),
- `clearence` - Клиренс (мм)
- `v_bag` - Объём багажника (л),
- `v_tank` - Объём топливного бака (л),
- `curb_weight` - Снаряжённая масса (кг),
- `gross_weight` - Полная масса (кг),
- `front_brakes` - Передние тормоза,
- `rear_brakes` - Задние тормоза,
- `max_speed` - Максимальная скорость (км/ч),
- `acceleration` - Разгон до 100 км/ч (с),
- `fuel_cons` - Расход топлива (л/100 км),
- `fuel_brand` - Марка топлива,
- `engine_loc1` - Расположение двигателя,
- `engine_loc2` - Ориентация двигателя,
- `turbocharg` - Турбина,
- `max_torq` - Максимальный крутящий момент (Н*м),
- `cyl_count` Количество цилиндров.

''')

if uploaded_file is not None:
    # Загрузим датасет.
    # Зададим типы данных в колонках.
    dtypes_of_data = {
        'url_car': str,
        'car_make': str,
        'car_model': str,
        'car_gen': str,
        'car_type': str,
        'car_compl': str,
        'ann_id': str,
        'car_price': float,
        'ann_city': str,
        'link_cpl': str,
        'avail': str,
        'year': int,
        'mileage': int,
        'color': str,
        'eng_size': float,
        'eng_power': float,
        'eng_power_kw': float,
        'eng_type': str,
        'pow_resrv': str,
        'options': str,
        'transmission': str,
        'drive': str,
        'st_wheel': str,
        'condition': str,
        'count_owner': str,
        'original_pts': str,
        'customs': str,
        'url_compl': str,
        'state_mark': str,
        'class_auto': str,
        'door_count': float,  # могут быть пропуски
        'seat_count': str,  # могут быть значения с диапазоном, пропуски
        'long': float,
        'width': float,
        'height': float,
        'clearence': str,  # могут быть значения с диапазоном
        'v_bag': str,  # могут быть значения с диапазоном, пропуски
        'v_tank': float,
        'curb_weight': float,
        'gross_weight': float,
        'front_brakes': str,
        'rear_brakes': str,
        'max_speed': float,
        'acceleration': float,
        'fuel_cons': float,
        'fuel_brand': str,
        'engine_loc1': str,
        'engine_loc2': str,
        'turbocharg': str,
        'max_torq': float,
        'cyl_count': float  # Могут быть пропуски
    }
    try:
        # Создаём датафрейм для анализа
        df = pd.read_csv(uploaded_file,
                     dtype=dtypes_of_data, parse_dates=['ann_date'])
    except:
        st.error('Ошибка загрузки файла. Проверьте правильность ввода файла')

    # Загружаем файл в серверную часть
    result = upload_file("api/v1/dataset/upload", uploaded_file)
    if result['message'] == "CSV dataset uploaded successfully":
        st.success("Файл успешно загружен и отправлен на сервер!")
    else:
        st.error('Ошибка отправки файла на сервер.')


    if df.shape[0] > 0:
        # Создадим столбец с максимальным
        # количеством мест и с минимальным
        df.loc[df['seat_count'].str.len() > 2, 'seat_count'] = \
            df[df['seat_count'].str.len() > 2]['seat_count'].str.split(', ').apply(
                lambda x: max(map(int, x)))

        # Клиренс с диапазоном значений заполним максимальным значением
        df.loc[df['clearence'].str.len() > 5, 'clearence'] = \
            df[df['clearence'].str.len() > 5]['clearence'].str.split('-').apply(
         lambda x: max(map(int, x)))

        # Объём багажника с диапазоном значений заполним максимальным значением
        df.loc[df['v_bag'].str.find('/') > 0, 'v_bag'] = \
            df[df['v_bag'].str.find('/') > 0]['v_bag'].str.split('/').apply(
                lambda x: max(map(int, x)))

        # Количество владельцев представим в виде чисел
        df.loc[df['count_owner'] == '1 владелец', 'count_owner'] = 1
        df.loc[df['count_owner'] == '2 владельца', 'count_owner'] = 2
        df.loc[df['count_owner'] == '3 или более', 'count_owner'] = 3

        # Удалим столбец eng_power_kw, т.к. он избыточный (имеется столбец с мощностью в л.с.)
        df.drop(['eng_power_kw'], axis=1, inplace=True)

        # Удалим признаки 'url_car', 'ann_id', 'link_cpl', 'url_compl'
        # они не представляют ценности для дальнейшего анализа
        df.drop(['url_car', 'ann_id', 'link_cpl', 'url_compl'], axis=1, inplace=True)

        # Удалим признак `condition`, который имеет одно значение.
        df.drop(['condition'], axis=1, inplace=True)

        # Удалим признак `gross_weight`, избыточный вместе с `curb_weight`
        df.drop(['gross_weight'], axis=1, inplace=True)

        # Составим список числовых признаков
        num_features = (
            df.select_dtypes(
                include=['int', 'float']
            ).columns.to_list()
        )

        message, select = st.columns(2, vertical_alignment="bottom")
        message.markdown('Выберите признак, распределение значений которого хотите изучить')

        feature_to_analize = select.selectbox('Признак', num_features)

        fig = go.Figure()
        fig.add_trace(go.Histogram(
                x=df[feature_to_analize],
                histnorm='percent',
                name=f'{feature_to_analize}',
                marker_color='#EB89B5'
            ))

        fig.update_layout(
            xaxis_title_text=f'Значения {feature_to_analize}',
            yaxis_title_text='Количество объектов',
            title_text=f'Распределение значений {feature_to_analize}',
            hovermode="x"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Определим значения признака, для которых будем считать среднее
        df['intervals'], thresholds = \
            pd.qcut(df[feature_to_analize], q=40, duplicates='drop', retbins=True)
        data = df.groupby(by=['intervals'],
                          observed=True)['car_price'].agg(['mean'])
        labels = (thresholds[1:] + thresholds[:-1]) / 2

        fig = go.Figure([
            go.Scatter(
                name='объекты',
                x=df[feature_to_analize],
                y=df['car_price'],
                mode='markers',
                line=dict(color='rgb(31, 119, 180)'),
            ),
            go.Scatter(
                name='среднее значение',
                x=labels,
                y=data['mean'],
                mode='markers',
                line=dict(color='red'),
            )
        ])
        fig.update_layout(
            yaxis=dict(title=dict(text='Целевой признак (цена)')),
            title=dict(text=f'Значения {feature_to_analize}'),
            title_text=f'Связь {feature_to_analize} с целевым признаком (цена)',
            hovermode="x"
        )
        st.plotly_chart(fig, use_container_width=True)