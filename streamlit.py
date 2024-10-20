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
menu = st.sidebar.radio("Выберите график", ["График по профессиям", "Влияние опыта работы на зарплату", "3D Scatter Plot"])

# Отображаем выбранный график
if menu == "График по профессиям":
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
    fig_line = go.Figure()
    for education_level in salary_by_education_experience['Образование'].unique():
        subset = salary_by_education_experience[salary_by_education_experience['Образование'] == education_level]
        fig_line.add_trace(go.Scatter(
            x=subset['Опыт работы'],
            y=subset['Средняя зарплата'],
            mode='lines+markers',
            name=education_level,
            text=education_level,
            marker=dict(size=8)
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
    unique_categories = df['Категория'].unique()
    selected_categories = st.multiselect(
        'Выберите категории',
        options=unique_categories,
        default=unique_categories  # Изначально все категории выбраны
    )
    filtered_df = df[df['Категория'].isin(selected_categories)]
    
    # Определяем цветовую палитру
    colors = px.colors.qualitative.Plotly
    color_map = {category: colors[i % len(colors)] for i, category in enumerate(selected_categories)}

    # Создание 3D графика
    fig_3d = px.scatter_3d(
        filtered_df,
        x='Опыт работы',
        y='Образование',
        z='Средняя зарплата',
        color='Категория',
        title='3D Scatter Plot',
        hover_name='Категория',
        size_max=5,
        color_discrete_sequence=colors  # Используем цветовую палитру для 3D графика
    )

    # Установка пределов для осей (уменьшение зума на 50%)
    if filtered_df['Опыт работы'].dtype in ['int64', 'float64']:
        x_range = (filtered_df['Опыт работы'].min(), filtered_df['Опыт работы'].max())
        fig_3d.update_layout(
            scene=dict(
                xaxis=dict(range=[x_range[0] * 1.5, x_range[1] * 1.5])
            )
        )

    if filtered_df['Образование'].dtype in ['int64', 'float64']:
        y_range = (filtered_df['Образование'].min(), filtered_df['Образование'].max())
        fig_3d.update_layout(
            scene=dict(
                yaxis=dict(range=[y_range[0] * 1.5, y_range[1] * 1.5])
            )
        )

    if filtered_df['Средняя зарплата'].dtype in ['int64', 'float64']:
        z_range = (filtered_df['Средняя зарплата'].min(), filtered_df['Средняя зарплата'].max())
        fig_3d.update_layout(
            scene=dict(
                zaxis=dict(range=[z_range[0] * 1.5, z_range[1] * 1.5])
            )
        )

    # Устанавливаем высоту графика
    fig_3d.update_layout(
        height=800
    )

    # Отображение 3D графика в Streamlit
    st.plotly_chart(fig_3d)

    # Построение scatter plot для средней зарплаты по образованию для каждой выбранной категории
    fig_scatter = go.Figure()

    for category in selected_categories:
        filtered_salary_data = df[df['Категория'] == category]
        salary_by_education = filtered_salary_data.groupby('Образование')['Средняя зарплата'].mean().reset_index()

        # Добавление точек для каждой категории с соответствующим цветом
        fig_scatter.add_trace(go.Scatter(
            x=salary_by_education['Образование'],
            y=salary_by_education['Средняя зарплата'],
            mode='markers',
            name=category,
            marker=dict(size=10, color=color_map[category])  # Используем одинаковый цвет
        ))

    # Настройка графика
    fig_scatter.update_layout(
        title='Средняя зарплата по образованию для выбранных категорий',
        xaxis_title='Уровень образования',
        yaxis_title='Средняя зарплата',
        height=600,
        width=1200
    )

    # Отображение scatter plot
    st.plotly_chart(fig_scatter)
