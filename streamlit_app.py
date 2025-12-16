import streamlit as st
import plotly.express as px # type: ignore
import pandas as pd

st.title("🎈 Matriculas - LCN UFPI]")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)


df = pd.read_csv("https://drive.google.com/uc?export=download&id=1_urzrUF2XmxmoAkcGmNvY0OG-Y5csMmk", encoding='cp1252', sep=';')

# Menu lateral para filtrar por aluno
with st.sidebar:
    alunos = ['Todos'] + sorted(df['Nome'].dropna().unique().tolist())
    aluno_selecionado = st.selectbox("Selecione um aluno", alunos)

# Filtrar DataFrame se um aluno específico for selecionado
if aluno_selecionado != 'Todos':
    df = df[df['Nome'] == aluno_selecionado]

# Group by 'Turno' and 'Período' and count unique 'Matrícula'
enrollment_by_shift_period = df.groupby(['Turno', 'Período'])['Matrícula'].nunique().reset_index()

# Convert 'Período' to datetime for proper sorting
enrollment_by_shift_period['Período'] = pd.to_datetime(enrollment_by_shift_period['Período'])
enrollment_by_shift_period = enrollment_by_shift_period.sort_values(by=['Período', 'Turno'])

# Convert 'Período' to string in 'YYYY-MM' format for text axis
enrollment_by_shift_period['Período'] = enrollment_by_shift_period['Período'].dt.strftime('%Y-%m')

# Plotting the data with Plotly Express for stacked bars and hover functionality
fig = px.bar(
    enrollment_by_shift_period,
    x='Período',
    y='Matrícula',
    color='Turno',  # Differentiate bars by 'Turno'
    title='Quantidade de Matrículas por Turno e Período (Sobrepostas)',
    labels={'Matrícula': 'Número de Matrículas', 'Período': 'Período'},
    barmode='stack', # This ensures the bars are stacked
    hover_data={'Período': True, 'Matrícula': True, 'Turno': True} # Custom hover data, 'Período' is already string
)

# Ensure x-axis is treated as category type (text)
fig.update_xaxes(type='category')

# Adjust general layout to control bar width and overall plot width
# Setting bargap to a very small value and bargroupgap to 0 should make bars as wide as possible.
# Increasing the 'width' of the plot to provide more space for bars.
fig.update_layout(bargap=0.25, bargroupgap=0.0) # Adjusted bargap, bargroupgap, and added width

fig.show()