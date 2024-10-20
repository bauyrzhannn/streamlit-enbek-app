import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Загрузка данных
df = pd.read_csv("cleaned_enbek.csv")

# Расчет средней зарплаты по образованию и опыту работы
salary_by_education_experience = df.groupby(['Образование', 'Опыт работы', 'Категория']).apply(
    lambda x: pd.Series({
        'Средняя зарплата': (x['Средняя зарплата'] * x['Рабочих мест']).sum() / x['Рабочих мест'].sum() if x['Рабочих мест'].sum() > 0 else 0,
        'Общее количество рабочих мест': x['Рабочих мест'].sum()
    })
).reset_index()

# Конвертация столбцов 'Общее количество рабочих мест' и 'Средняя зарплата' в int
salary_by_education_experience['Общее количество рабочих мест'] = salary_by_education_experience['Общее количество рабочих мест'].astype(int)
salary_by_education_experience['Средняя зарплата'] = salary_by_education_experience['Средняя зарплата'].astype(int)

# Группировка данных для вакансий
trends_by_profession = df.groupby(['Название работы', 'Фильтрованные регионы'])['Рабочих мест'].sum().reset_index(name='Количество вакансий')
top_professions = trends_by_profession.sort_values(['Фильтрованные регионы', 'Количество вакансий'], ascending=[True, False]).groupby('Фильтрованные регионы').head(5)

# Заголовок приложения
st.title('Наиболее востребованные профессии по фильтрованным регионам')

# Добавление бокового меню с радио-кнопками
menu = st.sidebar.radio("Выберите график", ["График по профессиям", "Влияние опыта работы на зарплату"])

# Если выбран график по профессиям
if menu == "График по профессиям":
    # Выпадающий список для выбора регионов
    selected_regions = st.multiselect(
        'Выберите регион',
        options=top_professions['Фильтрованные регионы'].unique(),
        default=top_professions['Фильтрованные регионы'].unique()  # Изначально все регионы выбраны
    )

    # Фильтрация данных в зависимости от выбранных регионов
    filtered_data = top_professions[top_professions['Фильтрованные регионы'].isin(selected_regions)]

    # Построение первого графика (столбчатый)
    fig_bar = px.bar(
        filtered_data,
        x='Название работы',
        y='Количество вакансий',
        color='Фильтрованные регионы',
        title='Наиболее востребованные профессии по фильтрованным регионам',
        labels={'Количество вакансий': 'Количество вакансий', 'Название работы': 'Профессии'},
        height=800,
        width=2000
    )

    # Отображение первого графика в Streamlit
    st.plotly_chart(fig_bar)

# Если выбран график влияния опыта работы на зарплату
elif menu == "Влияние опыта работы на зарплату":
    # Построение второго графика (линейный)
    fig_line = go.Figure()

    # Добавление линий для каждого уровня образования
    for education_level in salary_by_education_experience['Образование'].unique():
        subset = salary_by_education_experience[salary_by_education_experience['Образование'] == education_level]
        fig_line.add_trace(go.Scatter(
            x=subset['Опыт работы'],
            y=subset['Средняя зарплата'],
            mode='lines+markers',
            name=education_level,
            text=education_level,  # Добавляем текст для каждого уровня образования
            marker=dict(size=8)  # Увеличиваем размер маркеров
        ))

    # Настройка второго графика
    fig_line.update_layout(
        title='Влияние опыта работы на среднюю зарплату в зависимости от образования',
        xaxis_title='Опыт работы (лет)',
        yaxis_title='Средняя зарплата',
        legend_title='Образование',
        height=800,
        width=1200
    )

    # Отображение второго графика в Streamlit
    st.plotly_chart(fig_line)
