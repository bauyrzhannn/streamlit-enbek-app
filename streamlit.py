import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import MarkerCluster, HeatMap
import branca
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных
df = pd.read_csv("main_enbek_cleaned.csv")

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
menu = st.sidebar.radio("Выберите график", ["График по профессиям", "Влияние опыта работы на зарплату", "3D Scatter Plot" , "Top 20 Regions by Number of Vacancies","Average Salary in Each Region in 2024",'Kazakhstan Map' ,"Education Level Requirements in Job Vacancies in 2024","Weighted Average Salary by Education Level in 2024","Average Salary Distribution by Work Schedule in 2024","Top 10 Companies with the Most Vacancies in 2024",'Relationship Between Job Category and Work Experience in 2024','The impact of work experience on average salary depending on education'])

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
    
    # Построение scatter plot для средней зарплаты по опыту работы для каждой выбранной категории
    fig_scatter1 = go.Figure()

    for category in selected_categories:
        filtered_salary_data = df[df['Категория'] == category]
        salary_by_experience = filtered_salary_data.groupby('Опыт работы')['Средняя зарплата'].mean().reset_index()

        # Добавление точек для каждой категории с соответствующим цветом
        fig_scatter1.add_trace(go.Scatter(
            x=salary_by_experience['Опыт работы'],
            y=salary_by_experience['Средняя зарплата'],
            mode='markers',
            name=category,
            marker=dict(size=10, color=color_map[category])  # Используем одинаковый цвет
        ))

    # Настройка scatter plot
    fig_scatter1.update_layout(
        title='Средняя зарплата по опыту работы для выбранных категорий',
        xaxis_title='Опыт работы',
        yaxis_title='Средняя зарплата',
        height=600,
        width=1200
    )

    # Отображение scatter plot
    st.plotly_chart(fig_scatter1)

elif menu == "Top 20 Regions by Number of Vacancies":
    jobs_by_city = df.groupby("Фильтрованные регионы")["Рабочих мест"].sum()
    top_cities = jobs_by_city.sort_values(ascending=False).head(20).reset_index()
    calm_colors_no_black = ['#A8DADC', '#457B9D', '#F1FAEE', '#F1C40F', '#F47C7C',
                            '#2A9D8F', '#264653', '#E9C46A', '#F4A261', '#F9C74F',
                            '#90BE6D', '#43AA8B', '#4D908E', '#577590', '#277DA1']
    
    fig = px.bar(
        top_cities,
        x='Фильтрованные регионы',
        y='Рабочих мест',
        title='Top 20 Regions by Number of Vacancies in 2024',
        labels={'Фильтрованные регионы': 'Region', 'Рабочих мест': 'Number of Vacancies'},
        text='Рабочих мест'
    )
    fig.update_traces(marker_color=calm_colors_no_black)
    fig.update_layout(
        height=900,
        title_font=dict(size=24, color='dimgray', family='Arial'),
        xaxis_title='Region',
        yaxis_title='Number of Vacancies',
        xaxis_tickangle=-45,
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        template='plotly_white',
        plot_bgcolor='rgba(245, 245, 245, 0.95)',
        font=dict(size=14, color='dimgray')
    )
    fig.update_traces(textposition='outside', textfont_size=12)
    st.plotly_chart(fig)

elif menu == "Average Salary in Each Region in 2024":
    # Группировка данных для вычисления средней зарплаты по регионам
    df["Средняя зарплата с учетом рабочих мест"] = df["Средняя зарплата"] * df["Рабочих мест"]

    # Группировка по регионам и расчет взвешенной средней зарплаты
    weighted_avg_salary = df.groupby("Фильтрованные регионы").apply(
        lambda x: x["Средняя зарплата с учетом рабочих мест"].sum() / x["Рабочих мест"].sum()
    )
    sorted_avg_salary = weighted_avg_salary.sort_values(ascending=False).head(20).reset_index()
    sorted_avg_salary.columns = ['Регион', 'Средняя зарплата']

    # Преобразование средней зарплаты в целые числа
    sorted_avg_salary['Средняя зарплата'] = sorted_avg_salary['Средняя зарплата'].astype(int)

    # Определение цветов для столбцов
    colors = [
    'lightcoral', 'lightblue', 'lightgreen', 'lightyellow', 'lightsalmon',
    'lightpink', 'lightgrey', 'lavender', 'lightcyan', 'lightgoldenrodyellow',
    'peachpuff', 'thistle', 'lavenderblush', 'honeydew', 'beige',
    'mistyrose', 'powderblue', 'seashell', 'aliceblue', 'wheat'
]

    # Создание бар-графика для отображения средней зарплаты по регионам с разными цветами
    fig_salary = px.bar(
        sorted_avg_salary,
        x='Регион',
        y='Средняя зарплата',
        title='Средняя зарплата по регионам в 2024 году',
        labels={'Регион': 'Регион', 'Средняя зарплата': 'Средняя зарплата'},
        text='Средняя зарплата'
    )

    # Настройка цветов для каждого столбца
    fig_salary.update_traces(marker_color=colors)

    # Настройки графика
    fig_salary.update_layout(
        height=800,
        title_font=dict(size=24, color='dimgray', family='Arial'),
        xaxis_title='Регион',
        yaxis_title='Средняя зарплата',
        xaxis_tickangle=-45,
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        template='plotly_white',
        plot_bgcolor='rgba(245, 245, 245, 0.95)',
        font=dict(size=14, color='dimgray')
    )
    st.plotly_chart(fig_salary)
    
elif menu == 'Kazakhstan Map':
    df["Средняя зарплата с учетом рабочих мест"] = df["Средняя зарплата"] * df["Рабочих мест"]

    # Группировка по регионам и расчет взвешенной средней зарплаты
    weighted_avg_salary = df.groupby("Фильтрованные регионы").apply(
        lambda x: x["Средняя зарплата с учетом рабочих мест"].sum() / x["Рабочих мест"].sum()
    )

    # Define city coordinates
    city_coords = { 
        'Область Абай': {'lat': 48.9434, 'lon': 80.1390}, 
        'Алматинская область': {'lat': 43.9368, 'lon': 76.8260}, 
        'Алматы': {'lat': 43.2380, 'lon': 76.8829}, 
        'Астана': {'lat': 51.169, 'lon': 71.449}, 
        'Атырауская область': {'lat': 47.9053, 'lon': 51.3781}, 
        'Акмолинская область': {'lat': 51.9165, 'lon': 69.4110}, 
        'Актюбинская область': {'lat': 48.7797, 'lon': 57.9974}, 
        'Западно-Казахстанская область': {'lat': 49.5568, 'lon': 50.2227}, 
        'Жамбылская область': {'lat': 44.4168, 'lon': 72.1341}, 
        'Область Жетісу': {'lat': 45.00, 'lon': 78.00}, 
        'Мангистауская область': {'lat': 44.5908, 'lon': 53.8500}, 
        'Павлодарская область': {'lat': 52.6509, 'lon': 76.7773}, 
        'Северо-Казахстанская область': {'lat': 53.9797, 'lon': 69.045}, 
        'Туркестанская область': {'lat': 42.2663, 'lon': 68.1431}, 
        'Шымкент': {'lat': 42.3205, 'lon': 69.5876}, 
        'Восточно-Казахстанская область': {'lat': 48.6130, 'lon': 84.71032}, 
        'Карагандинская область': {'lat': 48.1671, 'lon': 73.4729}, 
        'Костанайская область': {'lat': 52.0615, 'lon': 62.9372}, 
        'Кызылординская область': {'lat': 45.2058, 'lon': 63.9155}, 
        'Область Ұлытау': {'lat': 48.00, 'lon': 66.59}
    }
    jobs_by_city = df.groupby("Фильтрованные регионы")["Рабочих мест"].sum()

    # Using data from top_cities for the top 20 regions
    top_cities = jobs_by_city.sort_values(ascending=False).head(20).reset_index()
    max_jobs = top_cities["Рабочих мест"].max()
    min_jobs = top_cities["Рабочих мест"].min()

    # Create a color map with branca.colormap
    colormap = branca.colormap.linear.YlOrRd_09.scale(min_jobs, max_jobs)
    colormap.caption = 'Количество вакансий'

    # Create the map with a cleaner tile
    m = folium.Map(location=[48.0196, 66.9237], zoom_start=5, tiles="cartodb positron")

    # Add marker cluster
    marker_cluster = MarkerCluster().add_to(m)

    # Calculate weighted average salary
    weighted_avg_salary = df.groupby("Фильтрованные регионы").apply(
        lambda x: x["Средняя зарплата с учетом рабочих мест"].sum() / x["Рабочих мест"].sum()
    )

    # Prepare data for heatmap
    heat_data = []

    # Add markers to the map with variable sizes and enhanced tooltips
    for _, row in top_cities.iterrows():
        region = row['Фильтрованные регионы']
        jobs = row['Рабочих мест']
        
        if region in city_coords:
            coords = city_coords[region]
            color = colormap(jobs)  # Use colormap to set color based on jobs count
            avg_salary = weighted_avg_salary.get(region, "Нет данных")
            
            # Add data to heatmap
            heat_data.append([coords['lat'], coords['lon'], jobs])  # Add lat, lon, and weight (jobs)

            # Vary the marker radius based on job count
            radius = 8 + (jobs / max_jobs) * 12
            
            # Create a CircleMarker with enhanced tooltip and popup styling
            folium.CircleMarker(
                location=[coords['lat'], coords['lon']],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                tooltip=folium.Tooltip(f"<strong style='font-size:14px;'>{region}</strong><br><span style='font-size:12px;'>Вакансий: {int(jobs)}<br>Средняя зарплата: {int(avg_salary)} KZT</span>"),
                popup=folium.Popup(
                    html=f"<div style='text-align: center; font-size:14px;'><strong>{region}</strong><br><span style='font-size:12px;'>Вакансий: {int(jobs)}<br>Средняя зарплата: {int(avg_salary)} KZT</span></div>", 
                    parse_html=True
                )
            ).add_to(marker_cluster)

    # Add heatmap to the map
        HeatMap(heat_data, radius=20, max_zoom=13).add_to(m)

    # Add colormap and GeoJSON
    colormap.add_to(m)
    folium.GeoJson('kz (1).json', style_function=lambda feature: {
        'fillColor': 'transparent',
        'color': 'blue',
        'weight': 1,
        'fillOpacity': 0.1
    }).add_to(m)

    # Save the map and display it
    m.save("kazakhstan_vacancies_map.html")
    st.title("Карта вакансий в Казахстане")
    st_folium(m, width=725)
elif menu == "Education Level Requirements in Job Vacancies in 2024":
# Calculate education level percentages
    education_counts = df["Образование"].value_counts()
    education_percentage = (education_counts / education_counts.sum()) * 100

    # Create the pie chart using Plotly
    fig = go.Figure(
        data=[
            go.Pie(
                labels=education_percentage.index,
                values=education_percentage,
                textinfo='percent+label',
                marker=dict(colors=px.colors.qualitative.Pastel),  # Use a pastel color palette
            )
        ]
    )

    # Update layout for background color and title styling
    fig.update_layout(
        title="Education Level Requirements in Job Vacancies in 2024",
        title_font=dict(size=24, color='black'),
        paper_bgcolor='white',  # Background of the figure
        plot_bgcolor='black'    # Background of the plot area
    )

    st.plotly_chart(fig)
elif menu=="Weighted Average Salary by Education Level in 2024":
    df["Средняя зарплата с учетом рабочих мест"] = df["Средняя зарплата"] * df["Рабочих мест"]

    # Группировка по образованию и вычисление взвешенной средней зарплаты
    weighted_avg_salary_by_education = df.groupby("Образование").apply(
        lambda x: x["Средняя зарплата с учетом рабочих мест"].sum() / x["Рабочих мест"].sum()
    )
    muted_colors = ['#7D9A9B', '#A6C8D7', '#E6D6C1', '#D9B08D', '#A4B6A8', '#B0B0B0']  # Added fifth color

    # Преобразование результата в int
    weighted_avg_salary_by_education = weighted_avg_salary_by_education.astype(int)
    fig = go.Figure(
    data=[
        go.Bar(
            x=weighted_avg_salary_by_education.index,
            y=weighted_avg_salary_by_education.values,
            marker=dict(color=muted_colors[:len(weighted_avg_salary_by_education.index)]),
            text=[f'{int(salary):,}' for salary in weighted_avg_salary_by_education.values],
            textposition='outside'
        )
    ]
)

    # Update layout for title, labels, and styling
    fig.update_layout(
        title="Weighted Average Salary by Education Level in 2024",
        title_font=dict(size=18, color='black'),
        xaxis_title="Education Level",
        yaxis_title="Average Salary (in KZT)",
        xaxis_tickangle=-45,  # Rotate x-axis labels for readability
        template='plotly_white',  # Clean grid background
        height=700,  # Set figure height for better readability
    )

    # Streamlit application
    st.title("Salary Analysis")
    st.plotly_chart(fig)
elif menu == 'Average Salary Distribution by Work Schedule in 2024':
    

# Расширенная профессиональная цветовая палитра
    extended_professional_colors = [
        '#1F77B4',  # Синий
        '#FF7F0E',  # Оранжевый
        '#2CA02C',  # Зеленый
        '#D62728',  # Красный
        '#9467BD',  # Пурпурный
        '#8C564B',  # Коричневый
        '#E377C2'   # Розовый
    ]

    # Создаем box plot с расширенной палитрой цветов
    fig = px.box(df, 
                x='График работы', 
                y='Средняя зарплата', 
                title='Распределение средней зарплаты по графику работы в 2024',
                labels={'График работы': 'График работы', 'Средняя зарплата': 'Средняя зарплата'},
                template='plotly_white',
                color='График работы',  # Группируем по графику работы
                color_discrete_sequence=extended_professional_colors)

    # Обновляем внешний вид
    fig.update_layout(
        xaxis_title='График работы',
        yaxis_title='Средняя зарплата',
        xaxis_tickangle=-45,  # Поворот подписей по оси X для лучшей читаемости
        height=800  # Увеличение высоты графика
    )

    # Заголовок приложения Streamlit
    st.title("Анализ Зарплат по Графикам Работы")

    # Показываем график
    st.plotly_chart(fig)

elif menu == 'Top 10 Companies with the Most Vacancies in 2024':

    top_companies = df.groupby("Название компаний")["Рабочих мест"].sum().sort_values(ascending=False)

    # Выбор топ-10 компаний
    top_5_companies = top_companies.head(10)

    # Создание столбчатой диаграммы с помощью Plotly
    fig = px.bar(top_5_companies, 
                x=top_5_companies.values, 
                y=top_5_companies.index, 
                orientation='h',  # Горизонтальные столбцы
                labels={'y': 'Название компании', 'x': 'Общее количество вакансий'}, 
                title='Топ 10 компаний с наибольшим количеством вакансий в 2024',
                text=top_5_companies.values,  # Добавляем значения на график
                color=top_5_companies.index,  # Цвета в зависимости от компании
                color_discrete_sequence=px.colors.qualitative.Pastel)  # Пастельная цветовая схема

    # Настройка отображения текста и внешнего вида
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')

    # Обновляем макет графика
    fig.update_layout(
        xaxis_title='Общее количество вакансий',
        yaxis_title='Название компании',
        height=600,
        showlegend=False
    )

    # Заголовок приложения Streamlit
    st.title("Анализ Топ-10 Компаний по Вакансиям")

    # Показываем график
    st.plotly_chart(fig)
    
elif menu=='Relationship Between Job Category and Work Experience in 2024':
    df["Опыт работы"] = df["Опыт работы"].astype(int)

    # Создание сводной таблицы для подсчета вакансий по категориям и опыту работы
    pivot_table = pd.pivot_table(df, values='Название работы', index='Категория', columns='Опыт работы', aggfunc='count', fill_value=0)

    # Преобразование сводной таблицы в DataFrame для удобства визуализации в Plotly
    pivot_table_reset = pivot_table.reset_index().melt(id_vars='Категория', var_name='Опыт работы', value_name='Количество вакансий')

    # Создание тепловой карты с использованием Plotly
    fig = px.imshow(pivot_table.values,
                    labels=dict(x="Опыт работы (в годах)", y="Категория", color="Количество вакансий"),
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    text_auto=True,  # Автоматически добавляет текстовые метки с числами
                    aspect="auto",   # Автоматически подстраивает размер карты
                    color_continuous_scale='Viridis')

    # Настройка заголовков и отображения
    fig.update_layout(
        title='Связь между категорией работы и опытом работы в 2024',
        xaxis_title='Опыт работы (в годах)',
        yaxis_title='Категория',
        height=700,
        width=1000
    )

    # Заголовок приложения Streamlit
    st.title("Анализ Вакансий по Категории и Опыт Работы")

    # Показываем график
    st.plotly_chart(fig)    
elif menu=='The impact of work experience on average salary depending on education':
    sns.lineplot(x='Опыт работы', y='Средняя зарплата', hue='Образование', data=salary_by_education_experience, marker='o')

    # Настройка графика
    plt.title('Влияние опыта работы на среднюю зарплату в зависимости от образования')
    plt.xlabel('Опыт работы (лет)')
    plt.ylabel('Средняя зарплата')
    plt.legend(title='Образование')
    plt.grid(True)

    # Отображение графика в Streamlit
    st.pyplot(plt)              
