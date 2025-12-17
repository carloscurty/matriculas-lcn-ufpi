import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

# 1. Configuração da Página (Deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="Dashboard Acadêmico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS globais
st.markdown("""
<style>
    .stApp {
        background-color: rgba(0,0,0,0.05);
    }
    /* Ajuste para remover padding extra do topo */
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Marcador para o botão 'Voltar ao Topo'
st.markdown("<span id='topo'></span>", unsafe_allow_html=True)

# 3. Função de Carregamento com Cache (Melhora drástica de performance)
@st.cache_data
def carregar_dados():
    url = "https://drive.google.com/uc?export=download&id=1_urzrUF2XmxmoAkcGmNvY0OG-Y5csMmk"
    df = pd.read_csv(url, encoding='cp1252', sep=';')
    
    # Tratamento inicial de dados
    # Converter Período para datetime apenas uma vez
    if 'Período' in df.columns:
        df['Período_dt'] = pd.to_datetime(df['Período'], errors='coerce')
        df['Período_str'] = df['Período_dt'].dt.strftime('%Y-%m')
    
    return df

# 4. Função auxiliar para gerar o HTML dos Cards (Evita repetição de código)
def exibir_card(titulo, valor, prefixo="", sufixo=""):
    return f"""
    <div style="
        padding: 15px; 
        border: 1px solid #112333; 
        background-color: #f0f0f0; 
        border-radius: 8px; 
        text-align: center;
        box-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);
        margin-bottom: 10px;">
        <h5 style="margin:0; font-size: 1rem; color: #333;">{titulo}</h5>
        <h3 style="margin:0; font-size: 1.5rem; font-weight: bold;">{prefixo}{valor}{sufixo}</h3>
    </div>
    """

# 5. Função para colorir tabela (Sem dependência de Matplotlib)
def cor_condicional(valor, cor_hex):
    if isinstance(valor, (int, float)) and valor > 0:
        return f'background-color: {cor_hex}'
    return ''

# --- INÍCIO DO APP ---

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Ciências da Natureza/UFPI")
    
    # Filtros
    st.subheader("Filtros")
    alunos = ['Todos'] + sorted(df['Nome'].dropna().unique().tolist())
    aluno_selecionado = st.selectbox("Selecione um aluno", alunos)

    periodos = sorted(df['Período'].dropna().unique().tolist())
    periodo_selecionado = st.multiselect("Selecione períodos", periodos, default=periodos)

    # Navegação
    st.markdown("""
        <h1 style='font-size: 18px; margin-bottom: 5px; padding-bottom: 0;'>Navegação</h1>
        <hr style='margin-top: 2px; margin-bottom: 20px; border: 1px solid #ccc;'>
    """, unsafe_allow_html=True)
    
    estilo_link = "font-size: 14px; text-decoration: none; color: inherit; display: block; margin-bottom: 10px;"
    st.markdown(f"""
        <a href="#total-de-alunos" style="{estilo_link}">📝 Métricas Gerais</a>
        <a href="#melhores-alunos" style="{estilo_link}">✅ Aprovações (Top 10)</a>
        <a href="#graficos" style="{estilo_link}">📊 Gráficos</a>
        <a href="#relacao-geral-de-alunos" style="{estilo_link}">👥 Relação Geral</a>
    """, unsafe_allow_html=True)

# Aplicação dos Filtros
df_filtrado = df.copy()

if aluno_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Nome'] == aluno_selecionado]

if periodo_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Período'].isin(periodo_selecionado)]

# --- CÁLCULOS DAS MÉTRICAS ---
turnos = sorted(df_filtrado['Turno'].dropna().unique().tolist())
num_turnos = len(turnos)

if num_turnos == 0:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# Cálculos agregados baseados no DF filtrado
total_por_turno = df_filtrado.groupby('Turno')['Matrícula'].nunique()
media_por_turno = df_filtrado.groupby(['Turno', 'Período'])['Matrícula'].nunique().groupby('Turno').mean()
totgeral_por_turno = df_filtrado.groupby('Turno').size() # Contagem total de registros
aprovados_por_turno = (df_filtrado.groupby('Turno')['AP'].sum() / df_filtrado.groupby('Turno')['Total'].sum() * 100).fillna(0)

# --- VISUALIZAÇÃO: CARDS ---
st.markdown("<span id='metricas-gerais'></span>", unsafe_allow_html=True)

# Se for um aluno específico, mostra um layout simplificado
if aluno_selecionado != 'Todos':
    st.subheader(f"Resumo: {aluno_selecionado}")
    cols = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        with cols[i]:
            val = totgeral_por_turno.get(turno, 0)
            st.markdown(exibir_card(f"Matrículas ({turno})", val), unsafe_allow_html=True)
else:
    # Layout completo para "Todos"
    st.subheader("Total de Alunos")
    cols1 = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        val = total_por_turno.get(turno, 0)
        with cols1[i]:
            st.markdown(exibir_card(turno, val), unsafe_allow_html=True)

    st.subheader("Média de Matrículas por Período")
    cols2 = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        val = media_por_turno.get(turno, 0)
        with cols2[i]:
            st.markdown(exibir_card(turno, f"{val:.1f}"), unsafe_allow_html=True)

    st.subheader("Total Geral de Matrículas (Soma de todos períodos)")
    cols3 = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        val = totgeral_por_turno.get(turno, 0)
        with cols3[i]:
            st.markdown(exibir_card(turno, val), unsafe_allow_html=True)

    st.subheader("Nível de Aprovação (% Total)")
    cols4 = st.columns(num_turnos)
    for i, turno in enumerate(turnos):
        val = aprovados_por_turno.get(turno, 0)
        with cols4[i]:
            st.markdown(exibir_card(turno, f"{val:.1f}", sufixo="%"), unsafe_allow_html=True)

st.markdown("---")

# --- TABELA TOP ALUNOS ---
st.markdown("<span id='tabela-aprovacoes'></span>", unsafe_allow_html=True)
st.subheader("Melhores Alunos")

# Prepara dados para tabela
df_agrupado = df_filtrado.groupby('Nome').agg({
    'Ingresso': 'first',
    'Turno': 'first',
    'Total': 'sum',
    'AP': 'sum',
    'RP': 'sum',
    'TR': 'sum'
}).reset_index().rename(columns={
    'AP': 'Aprov',
    'RP': 'Reprov',
    'TR': 'Tranc',
    'Total': 'Matr'
})

df_agrupado['% Aprov'] = (df_agrupado['Aprov'] / df_agrupado['Matr'] * 100).fillna(0)

# Ordenação e Seleção
top_alunos = df_agrupado.sort_values(by=['% Aprov', 'Matr'], ascending=[False, False]).head(10)
colunas_exibicao = ['Nome', 'Turno', 'Matr', 'Aprov', 'Reprov', '% Aprov']

# Estilização da Tabela
styler = top_alunos[colunas_exibicao].style.format({
    'Matr': '{:.0f}',
    'Aprov': '{:.0f}',
    'Reprov': '{:.0f}',
    '% Aprov': '{:.1f}%'
})

# Aplica cores (vermelho/verde)
styler = styler.applymap(lambda v: cor_condicional(v, '#ffcccc'), subset=['Reprov'])
styler = styler.applymap(lambda v: cor_condicional(v, '#ccffcc'), subset=['Aprov'])

st.dataframe(styler, use_container_width=True, hide_index=True)

st.markdown("---")

# --- GRÁFICOS ---
st.markdown("<span id='graficos'></span>", unsafe_allow_html=True)
st.subheader("Gráficos")

# Gráfico 1: Matrículas por Turno e Período
enrollment_by_shift = df_filtrado.groupby(['Turno', 'Período_str'])['Matrícula'].nunique().reset_index()
enrollment_by_shift = enrollment_by_shift.sort_values('Período_str')

fig = px.bar(
    enrollment_by_shift,
    x='Período_str',
    y='Matrícula',
    color='Turno',
    title='Matrículas por Turno e Período',
    labels={'Matrícula': 'Qtd Alunos', 'Período_str': 'Período'},
    barmode='group' # Mudei para group para facilitar comparação, use 'stack' se preferir empilhado
)
fig.update_layout(xaxis_type='category') # Garante ordem correta do texto
st.plotly_chart(fig, use_container_width=True)

col_g1, col_g2 = st.columns(2)

with col_g1:
    # Gráfico 2: Evolução de Ingressantes
    ingressantes = df_filtrado[df_filtrado['Ingressante'] == 1].groupby('Período_str')['Matrícula'].nunique().reset_index()
    ingressantes = ingressantes.sort_values('Período_str')
    
    if not ingressantes.empty:
        fig_line = px.area(ingressantes, x='Período_str', y='Matrícula', title='Evolução de Ingressantes')
        fig_line.update_layout(xaxis_type='category')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Sem dados de ingressantes para o filtro atual.")

with col_g2:
    # Gráfico 3: Pizza
    alunos_por_turno = df_filtrado.groupby('Turno')['Matrícula'].nunique()
    if not alunos_por_turno.empty:
        fig_pie = px.pie(values=alunos_por_turno.values, names=alunos_por_turno.index, title='Distribuição por Turno')
        st.plotly_chart(fig_pie, use_container_width=True)

# Gráfico 4: Status Acadêmico
status_df = df_filtrado.groupby('Período_str')[['AP', 'RP', 'TR']].sum().reset_index()
status_df = status_df.sort_values('Período_str')
status_melted = status_df.melt(id_vars='Período_str', value_vars=['AP', 'RP', 'TR'], var_name='Status', value_name='Quantidade')

fig_bar_status = px.bar(
    status_melted, 
    x='Período_str', 
    y='Quantidade', 
    color='Status', 
    title='Status Acadêmico Absoluto (Aprov/Reprov/Tranc)', 
    barmode='stack',
    color_discrete_map={'AP': '#2ca02c', 'RP': '#d62728', 'TR': '#ff7f0e'} # Cores padrão (Verde, Vermelho, Laranja)
)
fig_bar_status.update_layout(xaxis_type='category')
st.plotly_chart(fig_bar_status, use_container_width=True)

st.markdown("---")

# --- RELAÇÃO GERAL ---
st.markdown("<span id='relacao-geral'></span>", unsafe_allow_html=True)
st.subheader("Relação Geral de Alunos")

# Usa o dataframe agrupado já calculado anteriormente
st.dataframe(df_agrupado.sort_values('Nome'), use_container_width=True, hide_index=True)

# --- RODAPÉ E BOTÃO TOPO ---
st.markdown("""
    <div style="text-align: center; margin-top: 30px; margin-bottom: 20px;">
        <a href='#topo' target="_self" style="text-decoration: none;">
            <button style="
                background-color: #f0f0f0; border: 1px solid black; border-radius: 8px; 
                padding: 10px 20px; cursor: pointer; font-weight: bold; color: black;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                ⬆ Voltar ao Topo
            </button>
        </a>
    </div>
""", unsafe_allow_html=True)

ano_atual = datetime.now().year
data_hoje = datetime.now().strftime("%d/%m/%Y")

st.markdown(f"""
<div style="text-align: center; padding-top: 20px; border-top: 1px solid #ccc; font-size: 14px; color: #666;">
    <p>© {ano_atual} Ciências da Natureza - UFPI<br>
    <span style="font-size: 12px;">Dados atualizados em: {data_hoje}</span></p>
</div>
""", unsafe_allow_html=True)