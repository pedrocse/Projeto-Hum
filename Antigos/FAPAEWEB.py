import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm


# Função para carregar os dados do Excel
@st.cache_data
def load_data(file_path):
    # Carrega o arquivo Excel usando pandas
    data = pd.read_excel(file_path)
    return data


# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard de Notas", layout="wide")

# Título do dashboard
st.title("Dashboard de Notas dos Alunos")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregue o arquivo Excel com as notas", type=["xlsx"])

if uploaded_file is not None:
    # Carrega os dados do arquivo Excel
    df = load_data(uploaded_file)

    # Exibe a tabela completa
    st.subheader("Tabela Completa de Notas")
    st.dataframe(df)

    # Criar abas no dashboard
    tab1, tab2 = st.tabs(["Visão Geral", "Busca de Aluno"])

    # Aba 1: Visão Geral
    with tab1:
        st.header("Visão Geral da Turma")
        st.write("Esta aba mostra a tabela completa de notas e um gráfico de barras geral.")

        # Gráfico de barras geral para todas as disciplinas
        st.subheader("Gráfico de Notas por Disciplina (Média da Turma)")
        mean_scores = df.drop(columns=["Numero", "Nome"]).mean()
        st.bar_chart(mean_scores)

    # Aba 2: Busca de Aluno
    with tab2:
        st.header("Busca de Aluno")
        st.write("Esta aba permite buscar um aluno específico e visualizar seus gráficos.")

        # Input para o número do aluno
        numero_aluno = st.number_input("Insira o número do aluno", min_value=1, max_value=len(df), step=1)

        # Botão para buscar o aluno pelo número
        if st.button("Buscar Aluno"):
            # Filtrar os dados para o aluno selecionado pelo número
            aluno_df = df[df["Numero"] == numero_aluno]

            if not aluno_df.empty:
                aluno_selecionado = aluno_df.iloc[0]["Nome"]

                # Exibir informações do aluno selecionado
                st.subheader(f"Notas do Aluno: {aluno_selecionado}")
                st.dataframe(aluno_df)

                # Gráfico de barras para as notas do aluno por disciplina
                st.subheader("Gráfico de Notas por Disciplina")
                notas_aluno = aluno_df.drop(columns=["Numero", "Nome"]).T
                notas_aluno.columns = ["Notas"]
                st.bar_chart(notas_aluno)

                # Extrair as notas do aluno (excluindo NaN)
                notas_aluno = notas_aluno.dropna()
                disciplinas = notas_aluno.index
                notas = notas_aluno.values.flatten()

                # Criar gráfico da distribuição normal com Plotly
                st.subheader("Distribuição Normal e Notas do Aluno")
                mean = 6  # Média da distribuição normal
                std_dev = 1  # Desvio padrão da distribuição normal
                x = np.linspace(mean - 4 * std_dev, mean + 4 * std_dev, 100)  # Valores no eixo x
                y = norm.pdf(x, mean, std_dev)  # Função de densidade de probabilidade

                # Criar o gráfico de distribuição normal
                fig = go.Figure()

                # Adicionar a curva normal
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name="Distribuição Normal",
                    line=dict(color="blue")
                ))

                # Adicionar os pontos das notas do aluno
                for disciplina, nota in zip(disciplinas, notas):
                    y_nota = norm.pdf(nota, mean, std_dev)  # Posição vertical na curva normal
                    fig.add_trace(go.Scatter(
                        x=[nota],
                        y=[y_nota],
                        mode="markers",
                        name=f"{disciplina}: {nota:.1f}",
                        marker=dict(color="red", size=10),
                        hoverinfo="text",
                        hovertext=f"Disciplina: {disciplina}<br>Nota: {nota:.1f}"
                    ))

                # Adicionar linhas tracejadas para os desvios padrão
                for i in range(-3, 4):  # De -3σ a +3σ
                    #if i != 0:  # Ignorar a linha da média (0σ)
                        x_line = mean + i * std_dev
                        y_line = norm.pdf(x_line, mean, std_dev)
                        fig.add_shape(
                            type="line",
                            x0=x_line, y0=0, x1=x_line, y1=y_line,
                            line=dict(color="red", width=2, dash="dash"),
                            name=f"{i}σ"
                        )
                        fig.add_annotation(
                            x=x_line, y=-0.02,
                            text=f"{i}σ",
                            showarrow=False,
                            yshift=10,
                            font=dict(color="red", size=10)
                        )

                # Configurações do gráfico
                fig.update_layout(
                    title="Distribuição Normal e Notas do Aluno",
                    xaxis_title="Notas",
                    yaxis_title="Densidade",
                    showlegend=False,
                    hovermode="closest",
                    plot_bgcolor="white",  # Fundo branco
                    height=600,  # Altura do gráfico (em pixels)
                    width=600,
                    xaxis=dict(
                        showgrid=True,  # Linhas de grade verticais
                        gridcolor="lightgray",  # Cor das linhas de grade
                        zeroline=True,  # Linha no eixo x = 0
                        zerolinecolor="gray"
                    ),
                    yaxis=dict(
                        showgrid=True,  # Linhas de grade horizontais
                        gridcolor="lightgray",  # Cor das linhas de grade
                        zeroline=True,  # Linha no eixo y = 0
                        zerolinecolor="gray",
                        range=[-0.05, 0.5]  # Fixar o eixo y entre 0 e 0.5 (ajuste para a PDF)
                    )
                )

                # Exibir o gráfico no Streamlit
                st.plotly_chart(fig)

            else:
                st.error("Aluno não encontrado. Verifique o número inserido.")

else:
    st.info("Por favor, faça o upload de um arquivo Excel para visualizar os dados.")