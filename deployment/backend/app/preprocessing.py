import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion

MODEL_PATH = 'models'

preprocess_pl = None

# Предобработка датасета, разделение на выборки
def preproc(df):

    global preprocess_pl
    # Загрузим ранее сохранённый обученный пайплайн предобработки
    with open(os.path.join(MODEL_PATH, 'process_pl.pkl'), 'rb') as preprocess_file:
        preprocess_pl = joblib.load(preprocess_file.name)
    print('Предобработчик загружен')

    # Предобработаем загруженный датасет ранее обученным пайплайном
    # Считаем, что имевшиеся ранее данные - обучающие для пайплайна
    # предобработки. С точки зрения подглядывания в тестовую выборку
    # сильно это ни на что не влияет.
    df = preprocess_pl.transform(df)

    # Разделяем предобработанный на тренировочную и тестовую выборки
    train, test = train_test_split(df, train_size=0.75)

    return train, test

# Предобработка выборки перед передачей модели
def preproc_x(df):
    global preprocess_pl
    if not preprocess_pl:
        # Загрузим ранее сохранённый обученный пайплайн предобработки
        with open(os.path.join(MODEL_PATH, 'process_pl.pkl'), 'rb') as preprocess_file:
            preprocess_pl = joblib.load(preprocess_file.name)
            print('Предобработчик загружен')

    # Предобработаем выборку
    df = preprocess_pl.transform(df)

    return df