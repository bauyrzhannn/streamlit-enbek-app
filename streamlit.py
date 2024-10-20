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

# Добавление бокового меню с кнопками
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "График по профессиям"

menu = st.sidebar.radio("Выберите график", ["График по профессиям", "Влияние опыта работы на зарплату", "3D Scatter Plot"])

# Отображаем выбранный график
if menu == "График по профессиям":
    st.session_state.selected_menu = "График по профессиям"
    # Код для графика по профессиям
    selected_regions = st.multiselect(
        'Выберите регион',
        options=top_professions['Фильтрованные регионы'].unique(),
        default=top_professions['Фильтрованные регионы'].unique()  # Изначально все регионы выбраны
    )
    filtered_data = top_professions[top_professions['Фильтрованные регионы'].isin(selected_regions)]
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
    st.plotly_chart(fig_bar)

elif menu == "Влияние опыта работы на зарплату":
    st.session_state.selected_menu = "Влияние опыта работы на зарплату"
    # Код для графика влияния опыта работы на зарплату
    fig_line = go.Figure()
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
    fig_line.update_layout(
        title='Влияние опыта работы на среднюю зарплату в зависимости от образования',
        xaxis_title='Опыт работы (лет)',
        yaxis_title='Средняя зарплата',
        legend_title='Образование',
        height=800,
        width=1200
    )
    st.plotly_chart(fig_line)

elif menu == "3D Scatter Plot":
    st.session_state.selected_menu = "3D Scatter Plot"
    # Код для 3D Scatter Plot
    unique_categories = df['Категория'].unique()
    selected_categories = st.multiselect(
        'Выберите категории',
        options=unique_categories,
        default=unique_categories  # Изначально все категории выбраны
    )
    filtered_df = df[df['Категория'].isin(selected_categories)]
    fig_3d = px.scatter_3d(
        filtered_df,
        x='Опыт работы',
        y='Образование',  # Измените на числовое значение, если есть
        z='Средняя зарплата',
        color='Категория',
        title='3D Scatter Plot',
        hover_name='Категория',
        size_max=5,  # Максимальный размер шариков
        color_discrete_sequence=px.colors.qualitative.Plotly  # Палитра цветов
    )

    # Установка пределов для осей (уменьшение зума на 50%)
    if filtered_df['Опыт работы'].dtype in ['int64', 'float64']:
        x_range = (filtered_df['Опыт работы'].min(), filtered_df['Опыт работы'].max())
        fig_3d.update_layout(
            scene=dict(
                xaxis=dict(range=[x_range[0] * 1.5, x_range[1] * 1.5])  # Уменьшаем диапазон по оси X
            )
        )

    if filtered_df['Образование'].dtype in ['int64', 'float64']:
        y_range = (filtered_df['Образование'].min(), filtered_df['Образование'].max())
        fig_3d.update_layout(
            scene=dict(
                yaxis=dict(range=[y_range[0] * 1.5, y_range[1] * 1.5])  # Уменьшаем диапазон по оси Y
            )
        )

    if filtered_df['Средняя зарплата'].dtype in ['int64', 'float64']:
        z_range = (filtered_df['Средняя зарплата'].min(), filtered_df['Средняя зарплата'].max())
        fig_3d.update_layout(
            scene=dict(
                zaxis=dict(range=[z_range[0] * 1.5, z_range[1] * 1.5])  # Уменьшаем диапазон по оси Z
            )
        )

    # Устанавливаем высоту графика
    fig_3d.update_layout(
        height=800  # Задайте желаемую высоту графика
    )

    # Отображение 3D графика в Streamlit
    st.plotly_chart(fig_3d)
