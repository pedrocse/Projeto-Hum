# streamlit run Media_TP_Sem_WEB_v03.py
from scipy.stats import norm
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json

# Configuração inicial do Streamlit
st.set_page_config(page_title="FAPEA", layout="wide")

# Função para carregar as credenciais do arquivo JSON
def load_credentials(file_path="credenciais.json"):
    with open(file_path, "r") as file:
        data = json.load(file)
    return {user["usuario"]: user["senha"] for user in data["usuarios"]}

CREDENCIAIS = load_credentials()

# Inicializa as variáveis do session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "df" not in st.session_state:
    st.session_state.df = None
if "bimestre" not in st.session_state:
    st.session_state.bimestre = ""

# Função para realizar o login
def login():
    st.subheader("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in CREDENCIAIS and CREDENCIAIS[usuario] == senha:
            st.session_state.logged_in = True
            st.success("Login realizado com sucesso!")
            st.rerun()  # Recarrega a página após o login
        else:
            st.error("Usuário ou senha incorretos.")

# Página principal do dashboard
def main():
    # Layout inicial
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Ferramenta de Análise do Processo de Ensino e Aprendizagem")
    with col2:
        st.image("campusHumanitas2.PNG", width=300)




    # Sidebar com configuração expansível
    # Sidebar com configuração expansível
    with st.sidebar:
        with st.expander("⚙️ Configuração", expanded=False):
            uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=["xlsx"])
            if uploaded_file:
                # Listar as planilhas disponíveis no arquivo Excel
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                selected_sheet = st.selectbox("Selecione a planilha:", sheet_names)

                bimestre = st.text_input("Bimestre:", placeholder="Ex: 1º Bimestre")
                if uploaded_file and bimestre.strip():
                    if st.button("Carregar Dados"):
                        # Carregar a planilha selecionada
                        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                        st.session_state.df = df
                        st.session_state.bimestre = bimestre
                        st.success(f"Dados carregados com sucesso da planilha '{selected_sheet}'!")


        # Opções de navegação (aparecem após configuração)
        if st.session_state.df is not None and st.session_state.bimestre:
            st.write("---")
            opcao = st.radio(
                "Selecione uma função:",
                [
                    "Visão Geral",
                    "Busca de Estudante",
                    "Estatísticas da Turma",
                    "Ranking de Estudante",
                    "Comparação de Estudante",
                    "Ranking por Disciplina",
                ],
            )

    # Conteúdo principal
    if st.session_state.df is not None and st.session_state.bimestre:
        df = st.session_state.df
        bimestre = st.session_state.bimestre

        if opcao == "Visão Geral":
            st.title("Visão Geral")
            # Conteúdo da visão geral
            st.write(f"Esta aba mostra a tabela completa de notas e um gráfico de barras geral para o {bimestre}.")

            # Exibe a tabela completa
            st.subheader("Tabela Completa de Notas")
            st.dataframe(df)

            # Gráfico de barras geral para todas as disciplinas
            st.subheader(f"Gráfico de Notas por Disciplina (Média da Turma) - {bimestre}")
            mean_scores = df.drop(columns=["Numero", "Nome"]).mean() # MAIS ANTIGO
            #mean_scores = df.drop(columns=["Numero", "Nome", "Total1 Final", "Total2 Final", "Total3 Final", "Total4 Final"]).mean()
            #numeric_columns = df.select_dtypes(include=[np.number]).columns
            #mean_scores = df[numeric_columns].mean()
            st.bar_chart(mean_scores)

            # Aba 2: Busca de Aluno
        elif opcao == "Busca de Estudante":
            st.title(f"Busca de Estudante - {bimestre}")
            # Campo de busca e checkboxes
            #nome_estudante = st.sidebar.text_input("Digite o nome do estudante:")
            #mostrar_detalhes = st.sidebar.checkbox("Mostrar detalhes completos")
            st.write(f"Esta aba permite buscar um estudante específico e visualizar seus gráficos para o {bimestre}.")

            # Input para o número do aluno
            numero_aluno = st.number_input("Insira o número do Estudante", min_value=1, max_value=len(df), step=1)

            # Botão para buscar o aluno pelo número
            if st.button("Buscar Estudante"):
                # Filtrar os dados para o aluno selecionado pelo número
                aluno_df = df[df["Numero"] == numero_aluno]

                if not aluno_df.empty:
                    aluno_selecionado = aluno_df.iloc[0]["Nome"]

                    # Exibir informações do aluno selecionado
                    st.subheader(f"Notas do Estudante: {aluno_selecionado}")
                    st.dataframe(aluno_df)

                    # Gráfico de barras para as notas do aluno por disciplina
                    st.subheader(f"Gráfico de Notas por Disciplina - {bimestre}")
                    notas_aluno = aluno_df.drop(columns=["Numero", "Nome"]).T
                    notas_aluno.columns = ["Notas"]
                    st.bar_chart(notas_aluno)

                    # Extrair as notas do aluno (excluindo NaN)
                    notas_aluno = notas_aluno.dropna()
                    disciplinas = notas_aluno.index
                    notas = notas_aluno.values.flatten()

                    # Criar gráfico da distribuição normal com Plotly
                    st.subheader(f"Distribuição Normal e Notas do Estudante - {bimestre}")
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

                    # Função para evitar sobreposição de pontos
                    def ajustar_posicao_vertical(notas):
                        # Dicionário para contar quantas vezes cada nota aparece
                        contagem_notas = {}
                        posicoes_y = []
                        for nota in notas:
                            if nota not in contagem_notas:
                                contagem_notas[nota] = 0
                            else:
                                contagem_notas[nota] += 0.5
                            # Ajuste incremental para evitar sobreposição
                            posicoes_y.append(norm.pdf(nota, mean, std_dev) + 0.02 * contagem_notas[nota])
                        return posicoes_y

                    # Ajustar posições verticais para evitar sobreposição
                    notas_ajustadas_y = ajustar_posicao_vertical(notas)

                    # Adicionar os pontos das notas do aluno
                    for disciplina, nota, y_nota in zip(disciplinas, notas, notas_ajustadas_y):
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
                        title=f"Distribuição Normal e Notas do Estudante - {bimestre}",
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
                    # Preparar dados Hexágono sem o Final score
                    disciplinas_filtradas = [disc for disc in disciplinas if disc != "Final score"]

                    # Filtrar as notas correspondentes às disciplinas filtradas
                    notas_filtradas = [nota for disc, nota in zip(disciplinas, notas) if disc != "Final score"]

                    # Fechar o hexágono (adicionar o primeiro elemento ao final)
                    disciplinas_hex = disciplinas_filtradas + [disciplinas_filtradas[0]]  # Fechar o hexágono
                    notas_hex = notas_filtradas + [notas_filtradas[0]]  # Fechar o hexágono com as notas correspondentes

                    # Criar o gráfico hexagonal
                    fig_hex = go.Figure()

                    fig_hex.add_trace(go.Scatterpolar(
                        r=notas_hex,
                        theta=disciplinas_hex,
                        fill='toself',
                        name='Desempenho do Estudante',
                        line=dict(color='blue', width=2),
                        marker=dict(color='red', size=8)
                    ))

                    # Configurações do gráfico
                    fig_hex.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 10],  # Ajuste conforme sua escala de notas
                                tickvals=[0, 2, 4, 6, 8, 10],
                                ticktext=["0", "2", "4", "6", "8", "10"],
                                tickfont=dict(color="black"),
                            ),
                            angularaxis=dict(
                                rotation=90,  # Começar no topo
                                direction='clockwise',
                                tickfont=dict(size=10)
                            )
                        ),
                        title=f'Distribuição de Habilidades - {aluno_selecionado}',
                        showlegend=True,
                        height=600,
                        margin=dict(l=50, r=50, t=50, b=50)
                    )

                    # Exibir o gráfico
                    st.plotly_chart(fig_hex, use_container_width=True)
                else:
                    st.error("Estudante não encontrado. Verifique o número inserido.")
            # Aba 3: Estatísticas da Turma
        elif opcao == "Estatísticas da Turma":
            st.title(f"Estatísticas da Turma - {bimestre}")
            # Checkbox para filtrar dados
            incluir_aprovados = st.sidebar.checkbox("Incluir apenas aprovados")
            st.write(f"Esta aba mostra estatísticas gerais da turma para o {bimestre}.")

            # Exibir média, mediana e desvio padrão por disciplina
            stats = df.drop(columns=["Numero", "Nome"]).agg(["mean", "median", "std"])
            st.dataframe(stats)

            # Gráfico de boxplot
            st.subheader(f"Boxplot das Notas da Turma - {bimestre}")
            fig_boxplot = go.Figure()
            for col in df.drop(columns=["Numero", "Nome"]).columns:
                fig_boxplot.add_trace(go.Box(y=df[col], name=col))
            fig_boxplot.update_layout(title=f"Boxplot das Notas - {bimestre}", height=600)
            st.plotly_chart(fig_boxplot)
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            mean_scores = df[numeric_columns].mean()
            #mean_scores = df.drop(columns=["Numero", "Nome", "Total1 Final", "Total2 Final", "Total3 Final", "Total4 Final"]).mean()
            #mean_scores = df.drop(columns=["Numero", "Nome"]).mean()
            disciplinas = mean_scores.index.tolist()
            medias = mean_scores.values.tolist()

            # Gráfico Hexagonal (Radar Chart)

            disciplinas_filtradas = [disc for disc in disciplinas if disc not in ["Numero", "Final score"]]
            medias = [med for disc, med in zip(disciplinas, medias) if disc not in ["Numero", "Final score"]]
            st.subheader(f"Visão Geral das Médias da Turma - {bimestre}")
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=medias + [medias[0]],
                theta=disciplinas_filtradas + [disciplinas_filtradas[0]],  # Fechar o hexágono
                fill='toself',
                name='Média da Turma',
                line=dict(color='blue', width=2),
                marker=dict(color='red', size=8)
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10],
                        tickvals=[0, 2, 4, 6, 8, 10],
                        tickfont=dict(color="black"),  # Adicione esta linha
                    ),
                ),
                title=f'Distribuição das Médias da Turma - {bimestre}',
                height=600
            )
            # Adicionamos a key única para o radar chart
            st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")

            # Gráfico de distribuição normal para cada disciplina
            st.subheader(f"Distribuição Normal das Notas da Turma - {bimestre}")
            disciplinas = df.drop(columns=["Numero", "Nome"]).columns

            for disciplina in disciplinas:
                # Filtrar as notas da disciplina selecionada
                notas_disciplina = df[disciplina].dropna()

                if not notas_disciplina.empty:
                    mean_disciplina = notas_disciplina.mean()  # Média das notas da disciplina
                    #mean_disciplina = 6
                    std_dev_disciplina = notas_disciplina.std()  # Desvio padrão das notas da disciplina
                    x_disciplina = np.linspace(mean_disciplina - 4 * std_dev_disciplina,
                                               mean_disciplina + 4 * std_dev_disciplina, 100)
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
                                contagem_notas[nota] += 0.5
                            # Ajuste incremental para evitar sobreposição
                            posicoes_y.append(
                                norm.pdf(nota, mean_disciplina, std_dev_disciplina) + 0.02 * contagem_notas[nota])
                        return posicoes_y


                    # Ajustar posições verticais para evitar sobreposição
                    notas_ajustadas_y = ajustar_posicao_vertical(notas_disciplina)

                    # Adicionar os pontos das notas dos alunos
                    for nome, nota, y_nota in zip(df["Nome"], notas_disciplina, notas_ajustadas_y):
                        fig_normal.add_trace(go.Scatter(
                            x=[nota],
                            y=[y_nota],
                            mode="markers",
                            name=f"{nome}: {nota:.1f}",
                            marker=dict(color="red", size=10),
                            hoverinfo="text",
                            hovertext=f"Estudante: {nome}<br>Nota: {nota:.1f}<br>Diferença da Média: {nota - mean_disciplina:.1f}"
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
                    #y_range_max =0.5

                    # Configurações do gráfico
                    fig_normal.update_layout(
                        title=f"Distribuição Normal das Notas em {disciplina} - {bimestre}",
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
                    # Calcular médias das disciplinas


            # Aba 4: Ranking de Alunos
        elif opcao == "Ranking de Estudante":
            st.title(f"Ranking de Estudantes - {bimestre}")
            # Checkbox para tipo de ranking
            ranking_por_nota = st.sidebar.checkbox("Ranking por média final")

            st.write(f"Esta aba classifica os estudantes com base na média geral para o {bimestre}.")

            # Calcular a média geral de cada aluno
            #df["Media_Geral"] = df.drop(columns=["Numero", "Nome"]).mean(axis=1) //calcula a média inclusive da coluna Final score
            #df["Media_Geral"] = df.drop(columns=["Numero", "Nome", "Final score"]).mean(axis=1)//calcula a média removendo a coluna Final score
            df["Media_Geral"] = df["Final score"]
            ranking = df[["Numero", "Nome","Final score"]].sort_values(by="Final score", ascending=False)# troquei Final score por Media_Geral

            # Exibir o ranking
            st.subheader(f"Ranking de Estudantes por Média Geral - {bimestre}")
            st.dataframe(ranking)

            # Gráfico de barras do ranking
            st.subheader(f"Gráfico de Barras do Ranking - {bimestre}")
            fig_ranking = go.Figure()
            fig_ranking.add_trace(go.Bar(
                x=ranking["Nome"],
                y=ranking["Final score"],# troquei Final score por Media_Geral
                marker_color="green"
            ))
            fig_ranking.update_layout(
                title=f"Ranking de Estudantes por Média Geral - {bimestre}",
                xaxis_title="Estudantes",
                yaxis_title="Final score",# troquei Final score por Media_Gera
                height=600
            )
            st.plotly_chart(fig_ranking)

            # Aba 5: Comparação de Alunos
        elif opcao == "Comparação de Estudante":
            st.title(f"Comparação de Estudantes - {bimestre}")
            # Multi-select para comparar alunos
            alunos_selecionados = st.sidebar.multiselect("Selecione alunos para comparar", ["Aluno 1", "Aluno 2"])
            st.write(f"Esta aba permite comparar as notas de dois ou mais estudantes para o {bimestre}.")

            # Selecionar alunos para comparação
            alunos_selecionados = st.multiselect("Selecione os estudantes para comparação", df["Nome"])

            if len(alunos_selecionados) >= 2:
                # Filtrar os dados dos alunos selecionados
                alunos_df = df[df["Nome"].isin(alunos_selecionados)].set_index("Nome").drop(columns=["Numero"])

                # Exibir as notas dos alunos selecionados
                st.subheader(f"Notas dos Estudantes Selecionados - {bimestre}")
                st.dataframe(alunos_df.T)

                # Gráfico de barras empilhadas
                st.subheader(f"Gráfico de Barras Empilhadas - {bimestre}")
                fig_comparacao = go.Figure()
                for aluno in alunos_selecionados:
                    fig_comparacao.add_trace(go.Bar(
                        x=alunos_df.columns,
                        y=alunos_df.loc[aluno],
                        name=aluno
                    ))
                fig_comparacao.update_layout(
                    title=f"Comparação de Notas dos Estudantes - {bimestre}",
                    xaxis_title="Disciplinas",
                    yaxis_title="Notas",
                    barmode="group",
                    height=600
                )
                st.plotly_chart(fig_comparacao)

            else:
                st.info("Selecione pelo menos dois estudantes para comparação.")

            # Aba 6: Ranking por Disciplina
        elif opcao == "Ranking por Disciplina":
            st.title(f"Ranking por Disciplina - {bimestre}")
            # Checkbox para disciplina específica
            disciplinas = df.drop(columns=["Numero", "Nome"]).columns
            disciplina_selecionada = st.sidebar.selectbox("Selecione a disciplina",disciplinas)
            #st.header(f"Ranking por Disciplina - {bimestre}")4
            st.write(f"Esta aba permite selecionar uma disciplina e visualizar as notas de todos os estudantes para o {bimestre}.")

            # Selecionar a disciplina
            #disciplinas = df.drop(columns=["Numero", "Nome"]).columns
            #disciplina_selecionada = st.selectbox("Selecione a disciplina", disciplinas)

            # Filtrar as notas da disciplina selecionada
            notas_disciplina = df[["Nome", disciplina_selecionada]].dropna()

            # Exibir o gráfico de barras
            st.subheader(f"Notas dos Estudantes em {disciplina_selecionada} - {bimestre}")
            fig_barras = go.Figure()
            fig_barras.add_trace(go.Bar(
                x=notas_disciplina["Nome"],
                y=notas_disciplina[disciplina_selecionada],
                marker_color="blue"
            ))
            fig_barras.update_layout(
                title=f"Notas dos Estudantes em {disciplina_selecionada} - {bimestre}",
                xaxis_title="Estudantes",
                yaxis_title="Notas",
                height=600
            )
            st.plotly_chart(fig_barras)

            # Gráfico de distribuição normal para a disciplina selecionada
            st.subheader(f"Distribuição Normal das Notas em {disciplina_selecionada} - {bimestre}")
            #mean_disciplina = notas_disciplina[disciplina_selecionada].mean()  # Média das notas da disciplina
            mean_disciplina = 5.82
            #std_dev_disciplina = 1
            std_dev_disciplina = notas_disciplina[disciplina_selecionada].std()  # Desvio padrão das notas da disciplina
            x_disciplina = np.linspace(mean_disciplina - 4 * std_dev_disciplina, mean_disciplina + 4 * std_dev_disciplina, 100)
            #x_disciplina = np.linspace(0,10, 100)
            #y_disciplina = norm.pdf(x_disciplina, mean_disciplina, std_dev_disciplina)
            y_disciplina = norm.pdf(x_disciplina, mean_disciplina, std_dev_disciplina)

            # Criar o gráfico de distribuição normal
            fig_normal = go.Figure()

            # Adicionar a curva normal com área preenchida
            fig_normal.add_trace(go.Scatter(
                x=x_disciplina,
                y=y_disciplina,
                mode="lines",
                name="Distribuição Normal",
                line=dict(color="rgba(135, 206, 250, 1)"),  # Mesma cor da área pre # Mesma cor da área preenchida
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
                        contagem_notas[nota] += 0.5
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
                    hovertext=f"Estudante: {nome}<br>Nota: {nota:.1f}<br>Diferença da Média: {nota - mean_disciplina:.1f}"
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
            #y_range_max = 0.5

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
# Verifica se o usuário está logado
if not st.session_state.logged_in:
    login()
else:
    main()
