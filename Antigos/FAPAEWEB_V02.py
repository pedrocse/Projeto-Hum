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

    # Criar abas no dashboard
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["Visão Geral", "Busca de Aluno", "Estatísticas da Turma", "Ranking de Alunos", "Comparação de Alunos", "Ranking por Disciplina"]
    )

    # Aba 1: Visão Geral
    with tab1:
        st.header("Visão Geral da Turma")
        st.write("Esta aba mostra a tabela completa de notas e um gráfico de barras geral.")

        # Exibe a tabela completa
        st.subheader("Tabela Completa de Notas")
        st.dataframe(df)

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

                # Adicionar a curva normal com área preenchida
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name="Distribuição Normal",
                    line=dict(color="rgba(135, 206, 250, 1)"),  # Mesma cor da área preenchida
                    fill="tozeroy",  # Preencher a área até y = 0
                    fillcolor="rgba(135, 206, 250, 0.5)"
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
                        hovertext=f"Disciplina: {disciplina}<br>Nota: {nota:.1f}<br>Diferença da Média: {nota - mean:.1f}"
                    ))

                # Adicionar linhas tracejadas para os desvios padrão
                for i in range(-3, 4):  # De -3σ a +3σ
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
                    height=800,  # Altura do gráfico (em pixels)
                    xaxis=dict(
                        showgrid=True,  # Linhas de grade verticais
                        gridcolor="lightgray",  # Cor das linhas de grade
                        zeroline=True,  # Linha no eixo x = 0
                        zerolinecolor="gray",
                        tickformat=".1f"  # Formatar valores no eixo x
                    ),
                    yaxis=dict(
                        showgrid=True,  # Linhas de grade horizontais
                        gridcolor="lightgray",  # Cor das linhas de grade
                        zeroline=True,  # Linha no eixo y = 0
                        zerolinecolor="gray",
                        range=[-0.05, 0.5],  # Fixar o eixo y entre 0 e 0.5 (ajuste para a PDF)
                        tickformat=".2f"  # Formatar valores no eixo y
                    )
                )

                # Exibir o gráfico no Streamlit
                st.plotly_chart(fig)

                # Botão para exportar dados do aluno
                if st.button("Exportar Dados do Aluno"):
                    st.download_button(
                        label="Clique para baixar",
                        data=aluno_df.to_csv(index=False),
                        file_name="dados_aluno.csv",
                        mime="text/csv"
                    )

            else:
                st.error("Aluno não encontrado. Verifique o número inserido.")

    # Aba 3: Estatísticas da Turma
    with tab3:
        st.header("Estatísticas da Turma")
        st.write("Esta aba mostra estatísticas gerais da turma.")

        # Exibir média, mediana e desvio padrão por disciplina
        stats = df.drop(columns=["Numero", "Nome"]).agg(["mean", "median", "std"])
        st.dataframe(stats)

        # Gráfico de boxplot
        st.subheader("Boxplot das Notas da Turma")
        fig_boxplot = go.Figure()
        for col in df.drop(columns=["Numero", "Nome"]).columns:
            fig_boxplot.add_trace(go.Box(y=df[col], name=col))
        fig_boxplot.update_layout(title="Boxplot das Notas", height=600)
        st.plotly_chart(fig_boxplot)

    # Aba 4: Ranking de Alunos
    with tab4:
        st.header("Ranking de Alunos")
        st.write("Esta aba classifica os alunos com base na média geral.")

        # Calcular a média geral de cada aluno
        df["Media_Geral"] = df.drop(columns=["Numero", "Nome"]).mean(axis=1)
        ranking = df[["Numero", "Nome", "Media_Geral"]].sort_values(by="Media_Geral", ascending=False)

        # Exibir o ranking
        st.subheader("Ranking de Alunos por Média Geral")
        st.dataframe(ranking)

        # Gráfico de barras do ranking
        st.subheader("Gráfico de Barras do Ranking")
        fig_ranking = go.Figure()
        fig_ranking.add_trace(go.Bar(
            x=ranking["Nome"],
            y=ranking["Media_Geral"],
            marker_color="green"
        ))
        fig_ranking.update_layout(
            title="Ranking de Alunos por Média Geral",
            xaxis_title="Alunos",
            yaxis_title="Média Geral",
            height=600
        )
        st.plotly_chart(fig_ranking)

    # Aba 5: Comparação de Alunos
    with tab5:
        st.header("Comparação de Alunos")
        st.write("Esta aba permite comparar as notas de dois ou mais alunos.")

        # Selecionar alunos para comparação
        alunos_selecionados = st.multiselect("Selecione os alunos para comparação", df["Nome"])

        if len(alunos_selecionados) >= 2:
            # Filtrar os dados dos alunos selecionados
            alunos_df = df[df["Nome"].isin(alunos_selecionados)].set_index("Nome").drop(columns=["Numero"])

            # Exibir as notas dos alunos selecionados
            st.subheader("Notas dos Alunos Selecionados")
            st.dataframe(alunos_df.T)

            # Gráfico de barras empilhadas
            st.subheader("Gráfico de Barras Empilhadas")
            fig_comparacao = go.Figure()
            for aluno in alunos_selecionados:
                fig_comparacao.add_trace(go.Bar(
                    x=alunos_df.columns,
                    y=alunos_df.loc[aluno],
                    name=aluno
                ))
            fig_comparacao.update_layout(
                title="Comparação de Notas dos Alunos",
                xaxis_title="Disciplinas",
                yaxis_title="Notas",
                barmode="group",
                height=600
            )
            st.plotly_chart(fig_comparacao)

        else:
            st.info("Selecione pelo menos dois alunos para comparação.")

    # Aba 6: Ranking por Disciplina
    # Aba 6: Ranking por Disciplina
    with tab6:
        st.header("Ranking por Disciplina")
        st.write("Esta aba permite selecionar uma disciplina e visualizar as notas de todos os alunos.")

        # Selecionar a disciplina
        disciplinas = df.drop(columns=["Numero", "Nome"]).columns
        disciplina_selecionada = st.selectbox("Selecione a disciplina", disciplinas)

        # Filtrar as notas da disciplina selecionada
        notas_disciplina = df[["Nome", disciplina_selecionada]].dropna()

        # Exibir o gráfico de barras
        st.subheader(f"Notas dos Alunos em {disciplina_selecionada}")
        fig_barras = go.Figure()
        fig_barras.add_trace(go.Bar(
            x=notas_disciplina["Nome"],
            y=notas_disciplina[disciplina_selecionada],
            marker_color="blue"
        ))
        fig_barras.update_layout(
            title=f"Notas dos Alunos em {disciplina_selecionada}",
            xaxis_title="Alunos",
            yaxis_title="Notas",
            height=600
        )
        st.plotly_chart(fig_barras)

        # Gráfico de distribuição normal para a disciplina selecionada
        st.subheader(f"Distribuição Normal das Notas em {disciplina_selecionada}")
        mean_disciplina = notas_disciplina[disciplina_selecionada].mean()  # Média das notas da disciplina
        std_dev_disciplina = notas_disciplina[disciplina_selecionada].std()  # Desvio padrão das notas da disciplina
        x_disciplina = np.linspace(mean_disciplina - 4 * std_dev_disciplina, mean_disciplina + 4 * std_dev_disciplina, 100)
        y_disciplina = norm.pdf(x_disciplina, mean_disciplina, std_dev_disciplina)

        # Criar o gráfico de distribuição normal
        fig_normal = go.Figure()

        # Adicionar a curva normal com área preenchida
        fig_normal.add_trace(go.Scatter(
            x=x_disciplina,
            y=y_disciplina,
            mode="lines",
            name="Distribuição Normal",
            line=dict(color="rgba(135, 206, 250, 1)"),  # Mesma cor da área preenchida
            fill="tozeroy",  # Preencher a área até y = 0
            fillcolor="rgba(135, 206, 250, 0.5)"
        ))

        # Função para evitar sobreposição de pontos
        def ajustar_posicao_vertical(notas):
            # Dicionário para contar quantas vezes cada nota aparece
            contagem_notas = {}
            posicoes_y = []
            for nota in notas:
                if nota not in contagem_notas:
                    contagem_notas[nota] = 0
                else:
                    contagem_notas[nota] += 0.2
                # Ajuste incremental para evitar sobreposição
                posicoes_y.append(norm.pdf(nota, mean_disciplina, std_dev_disciplina) + 0.02 * contagem_notas[nota])
            return posicoes_y

        # Ajustar posições verticais para evitar sobreposição
        notas_ajustadas_y = ajustar_posicao_vertical(notas_disciplina[disciplina_selecionada])

        # Adicionar os pontos das notas dos alunos
        for nome, nota, y_nota in zip(notas_disciplina["Nome"], notas_disciplina[disciplina_selecionada], notas_ajustadas_y):
            fig_normal.add_trace(go.Scatter(
                x=[nota],
                y=[y_nota],
                mode="markers",
                name=f"{nome}: {nota:.1f}",
                marker=dict(color="red", size=10),
                hoverinfo="text",
                hovertext=f"Aluno: {nome}<br>Nota: {nota:.1f}<br>Diferença da Média: {nota - mean_disciplina:.1f}"
            ))

        # Adicionar linhas tracejadas para os desvios padrão
        for i in range(-3, 4):  # De -3σ a +3σ
            x_line = mean_disciplina + i * std_dev_disciplina
            y_line = norm.pdf(x_line, mean_disciplina, std_dev_disciplina)
            fig_normal.add_shape(
                type="line",
                x0=x_line, y0=0, x1=x_line, y1=y_line,
                line=dict(color="red", width=2, dash="dash"),
                name=f"{i}σ"
            )
            fig_normal.add_annotation(
                x=x_line, y=-0.02,
                text=f"{i}σ",
                showarrow=False,
                yshift=10,
                font=dict(color="red", size=10)
            )

        # Ajuste automático do eixo y
        max_density = max(y_disciplina)  # Valor máximo da densidade da curva normal
        y_range_max = max_density * 1.2  # Adicionar 20% de margem para evitar achatamento

        # Configurações do gráfico
        fig_normal.update_layout(
            title=f"Distribuição Normal das Notas em {disciplina_selecionada}",
            xaxis_title="Notas",
            yaxis_title="Densidade",
            showlegend=False,
            hovermode="closest",
            plot_bgcolor="white",  # Fundo branco
            height=800,  # Altura do gráfico (em pixels)
            xaxis=dict(
                showgrid=True,  # Linhas de grade verticais
                gridcolor="lightgray",  # Cor das linhas de grade
                zeroline=True,  # Linha no eixo x = 0
                zerolinecolor="gray",
                tickformat=".1f"  # Formatar valores no eixo x
            ),
            yaxis=dict(
                showgrid=True,  # Linhas de grade horizontais
                gridcolor="lightgray",  # Cor das linhas de grade
                zeroline=True,  # Linha no eixo y = 0
                zerolinecolor="gray",
                range=[-0.05, y_range_max],  # Ajuste automático do eixo y
                tickformat=".2f"  # Formatar valores no eixo y
            )
        )

        # Exibir o gráfico no Streamlit
        st.plotly_chart(fig_normal)


else:
    st.info("Por favor, faça o upload de um arquivo Excel para visualizar os dados.")