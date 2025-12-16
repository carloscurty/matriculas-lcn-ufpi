import streamlit as st
import plotly.express as px # type: ignore
import pandas as pd

# Alterar cor de fundo da tela
st.markdown("""
<style>
.stApp {
    background-color: #010101;
}
</style>
""", unsafe_allow_html=True)

df = pd.read_csv("https://drive.google.com/uc?export=download&id=1_urzrUF2XmxmoAkcGmNvY0OG-Y5csMmk", encoding='cp1252', sep=';')

# Menu lateral para filtrar por aluno
with st.sidebar:
    st.sidebar.title("Ciências da Natureza/UFPI")
    st.sidebar.subheader("Matrículas")
    alunos = ['Todos'] + sorted(df['Nome'].dropna().unique().tolist())
    aluno_selecionado = st.selectbox("Selecione um aluno", alunos)

    periodos = sorted(df['Período'].dropna().unique().tolist())
    periodo_selecionado = st.multiselect("Selecione períodos", periodos, default=periodos)

    turnos = sorted(df['Turno'].dropna().unique().tolist())
    turno_selecionado = st.multiselect("Selecione turnos", turnos, default=turnos)

# Filtrar DataFrame se um aluno específico for selecionado
if aluno_selecionado != 'Todos':
    df = df[df['Nome'] == aluno_selecionado]

# Filtrar por períodos selecionados
if periodo_selecionado:
    df = df[df['Período'].isin(periodo_selecionado)]

# Filtrar por turnos selecionados
if turno_selecionado:
    df = df[df['Turno'].isin(turno_selecionado)]

# Calcular métricas por turno
total_por_turno = df.groupby('Turno')['Matrícula'].nunique()
media_por_turno = df.groupby(['Turno', 'Período'])['Matrícula'].nunique().groupby('Turno').mean()
totgeral_por_turno = df.groupby('Turno').size()

# Cards com métricas
turnos = list(total_por_turno.index)
num_turnos = len(turnos)

if aluno_selecionado == 'Todos':
    # Primeira linha: Total de alunos por turno
    st.subheader("Total de Alunos")
    cols1 = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        with cols1[i]:
            st.markdown(f"""
<div style="background-color: #112333; padding: 15px; border: #000000; border-radius: 8px; text-align: center;">
    <h5>{turno}</h5>
    <h3>{total_por_turno[turno]}</h3>
</div>
""", unsafe_allow_html=True)

    # Segunda linha: Média de matrículas por turno
    st.subheader("Média de Matrículas")
    cols2 = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        with cols2[i]:
            st.markdown(f"""
<div style="background-color: #112333; padding: 15px; border-radius: 8px; text-align: center;">
    <h5>{turno}</h5>
    <h3>{media_por_turno[turno]:.0f}</h3>
</div>
""", unsafe_allow_html=True)

    # Terceira linha: Total Geral de Matrículas
    st.subheader("Total Geral de Matrículas")
    cols3 = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        with cols3[i]:
            st.markdown(f"""
<div style="background-color: #112333; padding: 15px; border-radius: 8px; text-align: center;">
    <h5>{turno}</h5>
    <h3>{totgeral_por_turno[turno]}</h3>
</div>
""", unsafe_allow_html=True)
else:
    st.subheader(aluno_selecionado)
    cols = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        with cols[i]:
            st.markdown(f"""
<div style="background-color: #112333; padding: 15px; border-radius: 8px; text-align: center;">
    <h5>{turno}: {totgeral_por_turno[turno]} matrículas</h5>
</div>
""", unsafe_allow_html=True)

st.markdown("---")            

print("aaa")

# Novos cards sugeridos
st.subheader("Nível de Aprovação por Turno")
aprovados_por_turno = (df.groupby('Turno')['AP'].sum() / df.groupby('Turno')['Total'].sum() * 100).fillna(0)
cols_novos = st.columns(len(turnos))
for i, turno in enumerate(turnos):
    with cols_novos[i]:
            st.markdown(f"""
<div style="background-color: #112333; padding: 15px; border-radius: 8px; text-align: center;">
    <h5>{turno}</h5>
    <h3> {aprovados_por_turno.get(turno, 0):.1f}%</h3>
</div>
""", unsafe_allow_html=True)

#st.metric(f"{turno}", f"{aprovados_por_turno.get(turno, 0):.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# Tabela de Top Alunos
st.subheader("Melhores Alunos por Quantidade de Aprovações")

df_top10 = df.groupby('Nome').agg({
    'Ingresso': 'first',
    'Turno': 'first',
    'AP': 'sum',
    'RP': 'sum',
    'TR': 'sum',
    'Total': 'sum'
}).reset_index()
df_top10['% Aprov'] = (df_top10['AP'] / df_top10['Total'] * 100).fillna(0).round(0)
top_alunos = df_top10.nlargest(10, '% Aprov')[['Nome', 'Turno', 'AP', '% Aprov', 'Total']].reset_index(drop=True)
top_alunos = top_alunos.sort_values(by=['% Aprov', 'Total'], ascending=[False, False])
st.dataframe(top_alunos, hide_index=True)

st.markdown("---")   

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
    title='Matrículas por Turno e Período',
    labels={'Matrícula': 'Matrículas', 'Período': 'Período'},
    barmode='stack', # This ensures the bars are stacked
    hover_data={'Período': True, 'Matrícula': True, 'Turno': True} # Custom hover data, 'Período' is already string
)

# Ensure x-axis is treated as category type (text)
fig.update_xaxes(type='category')

# Adjust general layout to control bar width and overall plot width
# Setting bargap to a very small value and bargroupgap to 0 should make bars as wide as possible.
# Increasing the 'width' of the plot to provide more space for bars.
fig.update_layout(bargap=0.25, bargroupgap=0.0) # Adjusted bargap, bargroupgap, and added width

st.plotly_chart(fig)

# Novo gráfico: Evolução de Ingressantes por Período
#st.subheader("Evolução de Ingressantes por Período")
ingressantes_por_periodo = df[df['Ingressante'] == 1].groupby('Período')['Matrícula'].nunique().reset_index()
ingressantes_por_periodo['Período'] = pd.to_datetime(ingressantes_por_periodo['Período'])
ingressantes_por_periodo = ingressantes_por_periodo.sort_values('Período')
ingressantes_por_periodo['Período'] = ingressantes_por_periodo['Período'].dt.strftime('%Y-%m')
fig_line = px.area(ingressantes_por_periodo, x='Período', y='Matrícula', title='Evolução de Ingressantes por Período')
fig_line.update_xaxes(type='category')
st.plotly_chart(fig_line)

# Novo gráfico: Distribuição de Alunos por Turno
#st.subheader("Distribuição de Alunos por Turno")
alunos_por_turno = df.groupby('Turno')['Matrícula'].nunique()
fig_pie = px.pie(values=alunos_por_turno.values, names=alunos_por_turno.index, title='Distribuição de Alunos por Turno')
st.plotly_chart(fig_pie)

# Novo gráfico: Status Acadêmico por Turno (Barras Empilhadas)
#st.subheader("Status Acadêmico por Período")
status_df = df.groupby('Período')[['AP', 'RP', 'TR']].sum().reset_index()
status_df['Período'] = pd.to_datetime(status_df['Período'])
status_df = status_df.sort_values('Período')
status_df['Período'] = status_df['Período'].dt.strftime('%Y-%m')
status_melted = status_df.melt(id_vars='Período', value_vars=['AP', 'RP', 'TR'], var_name='Status', value_name='Count')
fig_bar_status = px.bar(status_melted, x='Período', y='Count', color='Status', title='Status Acadêmico por Período', barmode='stack')
fig_bar_status.update_xaxes(type='category')
st.plotly_chart(fig_bar_status)

st.markdown("---")

st.subheader("Relação de Alunos")

df_compactado = df_top10.sort_values(by=['Nome', 'Ingresso'], ascending=[True, True])
st.dataframe(df_compactado, hide_index=True)