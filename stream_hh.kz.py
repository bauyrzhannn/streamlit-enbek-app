import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import folium
from folium.plugins import MarkerCluster, HeatMap
import branca
from streamlit_folium import st_folium
st.set_page_config(layout="wide")

# Load and preprocess data
file = pd.read_csv('cleaned_hh.csv')

# Convert "Средняя зарплата (в тенге)" column to numeric
file["Средняя зарплата (в тенге)"] = pd.to_numeric(file["Средняя зарплата (в тенге)"], errors="coerce")

# Drop rows with NaN values in necessary columns
file = file.dropna(subset=["Средняя зарплата (в тенге)", "Категория"])
# Split the 'Тип занятости' column by the comma
file[['Тип занятости', 'График работы']] = file['Тип занятости'].str.split(',', expand=True)

# Remove any leading or trailing whitespace from the resulting columns
file['Тип занятости'] = file['Тип занятости'].str.strip()
file['График работы'] = file['График работы'].str.strip()

file['Рабочие места'] = file['Ссылка'].apply(lambda x: 1 if isinstance(x, str) else 0)

# Преобразуем столбец 'Рабочие места' в числовой тип
file['Рабочие места'] = pd.to_numeric(file['Рабочие места'], errors='coerce').fillna(0).astype(int)

# Check the first few rows to verify

# Streamlit layout
st.title('Analyzing data from headhunter.kz')

# Add sidebar menu with buttons
menu = st.sidebar.radio("Choose a chart", ["Most Popular Professions by Filtered Region", 
                                           '3D Scatter Plot',
                                         "Top 20 Regions by Number of Vacancies", "Average Salary in Each Region in 2024", 
                                          "Kazakhstan Map", 
                                          "Top 10 Companies with the Most Vacancies in 2024", 
                                          "Relationship Between Job Category and Work Experience in 2024",
                                          'Distribution of the average salary according to the work schedule in 2024',
                                          'Distribution of the Average Salary According to the Type of Employment in 2024'])

# Section for "Most Popular Professions by Filtered Regions"
if menu == "Most Popular Professions by Filtered Regions":
    salary_statistics_by_category = file.groupby("Категория")["Средняя зарплата (в тенге)"].agg(
        mean_salary="mean",
        median_salary="median",
        mode_salary=lambda x: x.mode()[0] if not x.mode().empty else None
    ).reset_index()

    salary_statistics_by_category["mean_salary"] = salary_statistics_by_category["mean_salary"].astype(int)
    salary_statistics_by_category["median_salary"] = salary_statistics_by_category["median_salary"].astype(int)
    salary_statistics_by_category["mode_salary"] = salary_statistics_by_category["mode_salary"].astype(float).astype(int)

    st.write("### Salary Statistics by Category")
    st.dataframe(salary_statistics_by_category)

    categories = salary_statistics_by_category["Категория"]
    mean_salary = salary_statistics_by_category["mean_salary"]
    median_salary = salary_statistics_by_category["median_salary"]
    mode_salary = salary_statistics_by_category["mode_salary"]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=categories, y=mean_salary, name='Mean Salary', marker_color='skyblue'))
    fig.add_trace(go.Bar(x=categories, y=median_salary, name='Median Salary', marker_color='lightgreen'))
    fig.add_trace(go.Bar(x=categories, y=mode_salary, name='Mode Salary', marker_color='salmon'))

    fig.update_layout(
        title='Average, Median, and Mode Salary by Category',
        xaxis_title='Category',
        yaxis_title='Salary (in Tenge)',
        xaxis_tickangle=-45,
        barmode='group',
        hovermode="x unified",
        width=1200,
        height=800
    )
    st.plotly_chart(fig)

# Section for "Top 20 Regions by Number of Vacancies"
elif menu == "Top 20 Regions by Number of Vacancies":
    jobs_by_city = file.groupby("Filter Регион")["Ссылка"].count().reset_index()
    jobs_by_city = jobs_by_city.rename(columns={"Ссылка": "Количество вакансий"})

    top_cities = jobs_by_city.sort_values(by='Количество вакансий', ascending=False).head(20).reset_index(drop=True)

    st.write("### Top 20 Regions by Number of Vacancies")
    st.dataframe(top_cities)

    fig = px.bar(top_cities, x='Filter Регион', y='Количество вакансий', title='Top 20 Regions by Number of Vacancies', 
                 labels={'Filter Регион': 'Region', 'Количество вакансий': 'Number of Vacancies'}, 
                 color='Количество вакансий', color_continuous_scale='YlOrRd')
    st.plotly_chart(fig)

# Section for "Kazakhstan Map"
elif menu == "Kazakhstan Map":
    # Define coordinates for cities
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

    # Process data for weighted average salary by region
    weighted_avg_salary = file.groupby("Filter Регион").apply(
        lambda x: (x["Средняя зарплата (в тенге)"] * x["Рабочие места"]).sum() / x["Рабочие места"].sum()
    ).reset_index(name="Средняя зарплата с учетом рабочих мест")
    weighted_avg_salary['Средняя зарплата с учетом рабочих мест'] = weighted_avg_salary['Средняя зарплата с учетом рабочих мест'].round().astype(int)


    # Map visualization
    jobs_by_city = file.groupby("Filter Регион")["Ссылка"].count().reset_index()
    jobs_by_city = jobs_by_city.rename(columns={"Ссылка": "Количество вакансий"})
    
    top_cities = jobs_by_city.sort_values(by='Количество вакансий', ascending=False).head(20).reset_index(drop=True)
    max_jobs = top_cities["Количество вакансий"].max()
    min_jobs = top_cities["Количество вакансий"].min()

    colormap = branca.colormap.linear.YlOrRd_09.scale(min_jobs, max_jobs)
    colormap.caption = 'Number of Vacancies'

    m = folium.Map(location=[48.0196, 66.9237], zoom_start=5, tiles="cartodb positron")
    marker_cluster = MarkerCluster().add_to(m)

    heat_data = []
    for _, row in top_cities.iterrows():
        region = row['Filter Регион']
        jobs = row['Количество вакансий']
        if region in city_coords:
            coords = city_coords[region]
            color = colormap(jobs)
            avg_salary = weighted_avg_salary.loc[weighted_avg_salary['Filter Регион'] == region, 'Средняя зарплата с учетом рабочих мест'].values[0]
            heat_data.append([coords['lat'], coords['lon'], jobs])

            # Calculate the radius of the marker based on the number of jobs
            radius = 8 + (jobs / max_jobs) * 12
            
            # Create a circle marker for each city
            folium.CircleMarker(
                location=[coords['lat'], coords['lon']],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                tooltip=folium.Tooltip(f"<strong>{region}</strong><br>Vacancies: {jobs}<br>Avg Salary: {avg_salary} KZT"),
                popup=folium.Popup(
                    html=f"<div style='text-align: center; font-size:14px;'><strong>{region}</strong><br><span style='font-size:12px;'>Vacancies: {jobs}<br>Avg Salary: {avg_salary} KZT</span></div>", 
                    parse_html=True
                )
            ).add_to(marker_cluster)

    # Add heatmap for vacancies density
    HeatMap(heat_data, radius=20, max_zoom=13).add_to(m)

    # Add the color scale to the map
    colormap.add_to(m)
    
    folium.GeoJson(
    'kz.json',
    name='Границы областей Казахстана',
    style_function=lambda feature: {
        'fillColor': 'transparent',
        'color': 'blue',
        'weight': 1,
        'fillOpacity': 0.1
    }
).add_to(m)

    # Display the map in Streamlit
    st.title("Vacancies Map of Kazakhstan")
    st_folium(m, width=725)
elif menu == 'Distribution of the average salary according to the work schedule in 2024':
    extended_professional_colors = [
    '#1F77B4',  # Blue
    '#FF7F0E',  # Orange
    '#2CA02C',  # Green
    '#D62728',  # Red
    '#9467BD',  # Purple
    '#8C564B',  # Brown
    '#E377C2'   # Pink
]

# Create the box plot with the extended color palette
    fig = px.box(
        file, 
        x='График работы', 
        y='Средняя зарплата', 
        title='Distribution of the Average Salary According to the Work Schedule in 2024',
        labels={'График работы': 'Work Schedule', 'Средняя зарплата': 'Average Salary'},
        template='plotly_white',
        color='График работы',  # Group by work schedule
        color_discrete_sequence=extended_professional_colors
    )

    # Update the layout for better readability
    fig.update_layout(
        xaxis_title='Work Schedule',
        yaxis_title='Average Salary',
        xaxis_tickangle=-45,  # Rotate X-axis labels for better readability
        height=800  # Increase the height of the chart
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

elif menu == 'Distribution of the Average Salary According to the Type of Employment in 2024':
    extended_professional_colors = [
    '#1F77B4',  # Blue
    '#FF7F0E',  # Orange
    '#2CA02C',  # Green
    '#D62728',  # Red
    '#9467BD',  # Purple
    '#8C564B',  # Brown
    '#E377C2'   # Pink
]

# Create the box plot with the extended color palette
    fig = px.box(
        file,
        x='Тип занятости',
        y='Средняя зарплата',
        title='Distribution of the Average Salary According to the Type of Employment in 2024',
        labels={'Тип занятости': 'Type of Employment', 'Средняя зарплата': 'Average Salary'},
        template='plotly_white',
        color='Тип занятости',  # Group by type of employmentAverage Salary Distribution by Work Schedule in 2024
        color_discrete_sequence=extended_professional_colors
    )

    # Update the layout for better readability
    fig.update_layout(
        xaxis_title='Type of Employment',
        yaxis_title='Average Salary',
        xaxis_tickangle=-45,  # Rotate X-axis labels for better readability
        height=800 ) # Increase the height of the chart
    st.plotly_chart(fig, use_container_width=True)
elif menu == 'Top 10 Companies with the Most Vacancies in 2024':
    top_companies = file.groupby("Название компаний")["Рабочие места"].sum().sort_values(ascending=False)

# Get the top 10 companies
    top_5_companies = top_companies.head(10)

    # Create the bar chart using Plotly
    fig = px.bar(
        top_5_companies,
        x=top_5_companies.values,
        y=top_5_companies.index,
        orientation='h',  # Horizontal bars
        labels={'y': 'Company Name', 'x': 'Total number of vacancies'},
        title='Top 10 Companies with the Most Vacancies in 2024',
        text=top_5_companies.values,  # Add values on the chart
        color=top_5_companies.index,  # Colors based on the company
        color_discrete_sequence=px.colors.qualitative.Pastel  # Pastel color scheme
    )

    # Customize text and layout
    fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')

    # Update chart layout
    fig.update_layout(
        xaxis_title='Total number of vacancies',
        yaxis_title='Company Name',
        height=600,
        showlegend=False
    )

    # Streamlit UI
    st.title("Top Companies with the Most Vacancies")

    # Display the DataFrame
    st.write("Data Overview:")
    st.dataframe(file)

    # Show the Plotly chart
    st.plotly_chart(fig)

elif menu == 'Relationship Between Job Category and Work Experience in 2024':
    # Convert the "Опыт работы (числовой)" column to integers
    file["Опыт работы (числовой)"] = file["Опыт работы (числовой)"].astype(int)

    # Map numeric experience values back to text labels for better readability
    experience_map = {0: 'не требуется', 1: '1–3 года', 2: '3–6 лет', 3: 'более 6 лет'}
    file['Опыт работы'] = file['Опыт работы (числовой)'].map(experience_map)

    # Create a pivot table for counting vacancies by category and work experience
    pivot_table = pd.pivot_table(
        file, 
        values='Название работы', 
        index='Категория', 
        columns='Опыт работы', 
        aggfunc='count', 
        fill_value=0
    )

    # Transform the pivot table into a DataFrame for easy visualization in Plotly
    pivot_table_reset = pivot_table.reset_index().melt(
        id_vars='Категория', 
        var_name='Опыт работы', 
        value_name='Количество вакансий'
    )

    # Create the heatmap using Plotly
    fig = px.imshow(
        pivot_table.values,
        labels=dict(x="Опыт работы (в годах)", y="Категория", color="Количество вакансий"),
        x=pivot_table.columns,
        y=pivot_table.index,
        text_auto=True,  # Automatically adds text labels with numbers
        aspect="auto",   # Automatically adjusts the size of the map
        color_continuous_scale='Viridis'
    )

    # Set titles and display settings
    fig.update_layout(
        title='Relationship Between Job Category and Work Experience in 2024',
        xaxis_title='Work experience (in years)',
        yaxis_title='Category',
        height=700,
        width=1000
    )

    # Streamlit app layout
    st.title("Job Market Analysis Dashboard")
    st.subheader("Relationship Between Job Category and Work Experience")

    # Show the heatmap in Streamlit
    st.plotly_chart(fig)


elif menu =='Average Salary in Each Region in 2024':
    salary_statistics_by_region = file.groupby("Filter Регион")["Средняя зарплата (в тенге)"].agg(
        mean_salary="mean", 
        median_salary="median", 
        mode_salary=lambda x: x.mode()[0] if not x.mode().empty else None
    ).reset_index()

    # Convert salaries to integers for better display
    salary_statistics_by_region["mean_salary"] = salary_statistics_by_region["mean_salary"].astype(int)
    salary_statistics_by_region["median_salary"] = salary_statistics_by_region["median_salary"].astype(int)

    # Sort data by mean salary in descending order and get the top 20 regions
    top_cities = salary_statistics_by_region.sort_values(by='mean_salary', ascending=False).head(20).reset_index(drop=True)

    # Define a color palette with 20 colors
    color_palette_20 = [
        '#A8DADC', '#457B9D', '#F1FAEE', '#F1C40F', '#F47C7C',
        '#2A9D8F', '#264653', '#E9C46A', '#F4A261', '#F9C74F',
        '#90BE6D', '#43AA8B', '#4D908E', '#577590', '#277DA1',
        '#D4E157', '#FFEB3B', '#FF7043', '#8BC34A', '#9C27B0'
    ]

    # Concatenate salary statistics (mean, median, and mode) into a single text field for better display
    top_cities['text'] = (
        '<br>Mean: ' + top_cities['mean_salary'].astype(str) + 
        '<br>Median: ' + top_cities['median_salary'].astype(str) + 
        '<br>Mode: ' + top_cities['mode_salary'].astype(str)
    )

    # First chart: Mean, Median, and Mode Salaries by Region
    fig1 = px.bar(
        top_cities,
        x='Filter Регион',
        y=["mean_salary", "median_salary", "mode_salary"],
        title='Salary Statistics by Region (Top 20)',
        labels={'Filter Регион': 'Region', 'value': 'Salary (in Tenge)'},
        barmode='group'  # Group bars for each region
    )

    # Update bar colors for fig1
    fig1.update_traces(marker_color=color_palette_20)
    fig1.update_layout(
        height=900,
        title_font=dict(size=24, color='dimgray', family='Arial'),
        xaxis_title='Region',
        yaxis_title='Salary (in Tenge)',
        xaxis_tickangle=-45,
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        template='plotly_white',
        plot_bgcolor='rgba(245, 245, 245, 0.95)',
        font=dict(size=14, color='dimgray')
    )
    fig1.update_traces(textposition='outside', text=top_cities['text'], textfont_size=12)

    # Second chart: Average Salary by Region
    fig2 = px.bar(
        top_cities,
        x='Filter Регион',
        y='mean_salary',
        title='Average Salary by Region (Top 20)',
        labels={'Filter Регион': 'Region', 'mean_salary': 'Average Salary (in Tenge)'},
        text='mean_salary'  # Displaying the average salary on the bars
    )

    # Update bar colors for fig2
    fig2.update_traces(marker_color=color_palette_20)
    fig2.update_layout(
        height=900,
        title_font=dict(size=24, color='dimgray', family='Arial'),
        xaxis_title='Region',
        yaxis_title='Average Salary (in Tenge)',
        xaxis_tickangle=-45,
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        template='plotly_white',
        plot_bgcolor='rgba(245, 245, 245, 0.95)',
        font=dict(size=14, color='dimgray')
    )
    fig2.update_traces(textposition='outside', textfont_size=12)

    # Streamlit app layout
    st.title("Regional Salary Statistics Dashboard")
    st.subheader("Mean, Median, and Mode Salaries by Region (Top 20)")
    st.plotly_chart(fig1)

    st.plotly_chart(fig2)
    
elif menu == 'Most Popular Professions by Filtered Region':

    profession_salary_stats = file.groupby(['Filter Регион', 'Название работы']).agg(
        Количество_вакансий=('Название работы', 'size'),
        Средняя_зарплата=('Средняя зарплата (в тенге)', 'mean'),
        Медиана_зарплата=('Средняя зарплата (в тенге)', 'median'),
        Мода_зарплата=('Средняя зарплата (в тенге)', lambda x: x.mode()[0] if not x.mode().empty else None)
    ).reset_index()

    # Сортировка и выбор топ-5 профессий для каждого региона
    top_5_professions_per_region = profession_salary_stats.sort_values(['Filter Регион', 'Количество_вакансий'], ascending=[True, False])
    top_5_professions_per_region = top_5_professions_per_region.groupby('Filter Регион').head(5).reset_index(drop=True)

    # Конкатенация статистики по зарплатам для отображения при наведении
    top_5_professions_per_region['Зарплата'] = (
        'Средняя: ' + top_5_professions_per_region['Средняя_зарплата'].round(0).astype(str) + '₸<br>' +
        'Медиана: ' + top_5_professions_per_region['Медиана_зарплата'].round(0).astype(str) + '₸<br>' +
        'Мода: ' + top_5_professions_per_region['Мода_зарплата'].fillna(0).round(0).astype(str) + '₸'
    )

    # Группировка данных для расчёта статистики по категориям
    category_salary_stats = file.groupby(['Filter Регион', 'Категория']).agg(
        Количество_вакансий=('Категория', 'size'),
        Средняя_зарплата=('Средняя зарплата (в тенге)', 'mean'),
        Медиана_зарплата=('Средняя зарплата (в тенге)', 'median'),
        Мода_зарплата=('Средняя зарплата (в тенге)', lambda x: x.mode()[0] if not x.mode().empty else None)
    ).reset_index()

    # Сортировка и выбор топ-5 категорий для каждого региона
    top_5_categories_per_region = category_salary_stats.sort_values(['Filter Регион', 'Количество_вакансий'], ascending=[True, False])
    top_5_categories_per_region = top_5_categories_per_region.groupby('Filter Регион').head(5).reset_index(drop=True)

    # Конкатенация статистики по зарплатам для отображения при наведении
    top_5_categories_per_region['Зарплата'] = (
        'Средняя: ' + top_5_categories_per_region['Средняя_зарплата'].round(0).astype(str) + '₸<br>' +
        'Медиана: ' + top_5_categories_per_region['Медиана_зарплата'].round(0).astype(str) + '₸<br>' +
        'Мода: ' + top_5_categories_per_region['Мода_зарплата'].fillna(0).round(0).astype(str) + '₸'
    )

    # Streamlit Layout
    st.title("Job Market Analysis by Region")

    # Отображение графика для профессий
    fig_profession = px.bar(
        top_5_professions_per_region,
        x='Количество_вакансий',
        y='Filter Регион',
        color='Название работы',
        title='Top 5 Most Popular Professions by Region with Salary Statistics',
        labels={'Filter Регион': 'Region', 'Количество_вакансий': 'Number of Vacancies', 'Название работы': 'Job Title'},
        orientation='h',
        hover_data={'Зарплата': True}  # Показывать статистику по зарплате при наведении
    )

    # Обновление параметров для лучшего восприятия
    fig_profession.update_layout(
        height=1000,
        width=2000,  # Увеличена ширина
        title_font=dict(size=24, color='dimgray', family='Arial'),
        xaxis_title='Number of Vacancies',
        yaxis_title='Region',
        yaxis=dict(showgrid=True, gridcolor='lightgrey', categoryorder='total ascending'),
        template='plotly_white',
        plot_bgcolor='rgba(245, 245, 245, 0.95)',
        font=dict(size=14, color='dimgray')
    )

    # Размещение текста снаружи столбцов
    fig_profession.update_traces(textposition='outside', textfont_size=12)

    # Отображение графика
    st.plotly_chart(fig_profession, use_container_width=True)

    # Отображение графика для категорий
    st.subheader("Top 5 Most Popular Categories by Region with Salary Statistics")
    fig_category = px.bar(
        top_5_categories_per_region,
        x='Количество_вакансий',
        y='Filter Регион',
        color='Категория',
        title='Top 5 Most Popular Categories by Region with Salary Statistics',
        labels={'Filter Регион': 'Region', 'Количество_вакансий': 'Number of Vacancies', 'Категория': 'Category'},
        orientation='h',
        hover_data={'Зарплата': True}  # Показывать статистику по зарплате при наведении
    )

    # Обновление параметров для лучшего восприятия
    fig_category.update_layout(
        height=1000,
        width=2000,  # Увеличена ширина
        title_font=dict(size=24, color='dimgray', family='Arial'),
        xaxis_title='Number of Vacancies',
        yaxis_title='Region',
        yaxis=dict(showgrid=True, gridcolor='lightgrey', categoryorder='total ascending'),
        template='plotly_white',
        plot_bgcolor='rgba(245, 245, 245, 0.95)',
        font=dict(size=14, color='dimgray')
    )

# Размещение текста снаружи столбцов
    fig_category.update_traces(textposition='outside', textfont_size=12)

    # Отображение графика
    st.plotly_chart(fig_category, use_container_width=True)
elif menu == '3D Scatter Plot':
    st.title("Job Market Data Visualization")
    st.subheader("Select Filters to Display the Graph")

    # Multiselect for Work Schedule (График работы)
    work_schedule = st.multiselect("Select Work Schedule", options=file['График работы'].unique(), default=file['График работы'].unique())
    
    # Multiselect for Employment Type (Тип занятости)
    employment_type = st.multiselect("Select Employment Type", options=file['Тип занятости'].unique(), default=file['Тип занятости'].unique())
    
    # Multiselect for Category (Категория)
    categories = st.multiselect("Select Categories", options=file['Категория'].unique(), default=file['Категория'].unique())
    
    # Filter data based on user selections
    filtered_data = file[(file['График работы'].isin(work_schedule)) & 
                         (file['Тип занятости'].isin(employment_type)) & 
                         (file['Категория'].isin(categories))]
    
    # Drop rows with missing values
    filtered_data.dropna(subset=['Средняя зарплата (в тенге)', 'Категория'], inplace=True)

    # Handle category color mapping
    unique_categories = file['Категория'].unique()
    color_palette = px.colors.qualitative.Alphabet  # A larger palette
    color_map = {cat: color_palette[i % len(color_palette)] for i, cat in enumerate(unique_categories)}

    # Create 3D scatter plot
    fig = px.scatter_3d(filtered_data, 
                        x='График работы',  # X-axis: Work Schedule
                        y='Средняя зарплата (в тенге)',  # Y-axis: Average Salary
                        z='Тип занятости',  # Z-axis: Employment Type
                        title="Work Schedule, Employment Type, Category, and Salary Comparison",
                        labels={'График работы': 'Work Schedule',
                                'Средняя зарплата (в тенге)': 'Average Salary (in tenge)',
                                'Тип занятости': 'Employment Type',
                                'Категория': 'Category or Profession'},
                        color='Категория',  # Color points based on Category
                        color_discrete_map=color_map)  # Apply the dynamic color map

    # Display the plot with a unique key
    st.plotly_chart(fig, key="work_schedule_plot")