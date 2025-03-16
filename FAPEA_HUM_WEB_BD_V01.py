from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm


# Configuração da conexão com o banco de dados
engine = create_engine('sqlite:///notas_alunos.db')

# Função para carregar dados de uma tabela específica
def load_data(table_name):
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)

# Carregar dados do banco de dados
df_alunos = load_data("alunos")
df_disciplinas = load_data("disciplinas")
df_notas = load_data("notas")

# Verificar os nomes das colunas
print("Colunas de df_alunos:", df_alunos.columns)
print("Colunas de df_disciplinas:", df_disciplinas.columns)
print("Colunas de df_notas:", df_notas.columns)

# Transformar os dados para o formato necessário
merged_df = (
    df_notas
    .merge(df_alunos, left_on="aluno_id", right_on="id")
    .merge(df_disciplinas, left_on="disciplina_id", right_on="id")
)
print("Colunas após o merge:", merged_df.columns)

# Ajustar os nomes das colunas, se necessário
merged_df.rename(columns={"nome_x": "nome", "nome_y": "disciplina"}, inplace=True)

# Criar o DataFrame final com pivot
df = (
    merged_df
    .pivot(index=["numero", "nome"], columns="disciplina", values="valor")
    .reset_index()
)
df.columns.name = None  # Remover o nome do índice das colunas

# Interface Streamlit
st.title("Ferramenta de Análise do Processo de Ensino e Aprendizagem")

# Entrada para o bimestre
bimestre = st.text_input("Digite o bimestre referente aos dados (ex.: 1º Bimestre):", value="")
if bimestre.strip() == "":
    st.warning("Por favor, insira o bimestre antes de continuar.")
else:
    # Criar abas no dashboard
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["Visão Geral", "Busca de Estudante", "Estatísticas da Turma", "Ranking de Estudante",
         "Comparação de Estudante", "Ranking por Disciplina", "BD"]
    )


    # Aba 1: Visão Geral
    with tab1:
        st.header(f"Visão Geral da Turma - {bimestre}")
        st.dataframe(df)

    # Aba 2: Busca de Estudante
    with tab2:
        st.header(f"Busca de Estudante - {bimestre}")
        st.write(f"Esta aba permite buscar um estudante específico e visualizar seus gráficos para o {bimestre}.")

        # Input para o número do aluno
        numero_aluno = st.number_input("Insira o número do Estudante", min_value=1, max_value=len(df), step=1)

        # Botão para buscar o aluno pelo número
        if st.button("Buscar Estudante"):
            # Filtrar os dados para o aluno selecionado pelo número
            aluno_df = df[df["numero"] == numero_aluno]
            if not aluno_df.empty:
                aluno_selecionado = aluno_df.iloc[0]["nome"]
                st.subheader(f"Notas do Estudante: {aluno_selecionado}")
                st.dataframe(aluno_df)

                # Extrair as notas do aluno (excluindo NaN)
                notas_aluno = aluno_df.drop(columns=["numero", "nome"]).values.flatten()
                notas_aluno = notas_aluno[~np.isnan(notas_aluno)]  # Remover valores NaN

                if len(notas_aluno) > 0:
                    # Calcular média das notas do aluno
                    mean = np.mean(notas_aluno)

                    # Criar o histograma
                    fig_histograma = go.Figure()

                    # Adicionar barras para cada disciplina
                    disciplinas = aluno_df.drop(columns=["numero", "nome"]).columns
                    fig_histograma.add_trace(go.Bar(
                        x=disciplinas,
                        y=notas_aluno,
                        name="Notas por Disciplina",
                        marker_color="blue"
                    ))

                    # Adicionar linha tracejada horizontal para a média
                    fig_histograma.add_shape(
                        type="line",
                        x0=disciplinas[0],  # Início do eixo X
                        y0=mean,  # Valor da média no eixo Y
                        x1=disciplinas[-1],  # Fim do eixo X
                        y1=mean,  # Valor da média no eixo Y
                        line=dict(color="red", width=2, dash="dash"),
                        name="Média"
                    )

                    # Anotação para a média
                    fig_histograma.add_annotation(
                        x=disciplinas[len(disciplinas) // 2],  # Posiciona no meio do eixo X
                        y=mean,
                        text=f"Média: {mean:.2f}",
                        showarrow=False,
                        font=dict(color="red", size=12),
                        yshift=10
                    )

                    # Configurações do histograma
                    fig_histograma.update_layout(
                        title=f"Histograma das Notas de {aluno_selecionado}",
                        xaxis_title="Disciplinas",
                        yaxis_title="Notas",
                        showlegend=False,
                        bargap=0.1  # Espaçamento entre as barras
                    )

                    # Exibir o histograma
                    st.subheader("Histograma das Notas")
                    st.plotly_chart(fig_histograma)

                    # Gráfico 2: Distribuição Normal
                    fig_normal = go.Figure()

                    # Curva de distribuição normal
                    std_dev = np.std(notas_aluno)
                    x = np.linspace(mean - 4 * std_dev, mean + 4 * std_dev, 100)
                    y = norm.pdf(x, mean, std_dev)
                    fig_normal.add_trace(go.Scatter(
                        x=x,
                        y=y,
                        mode="lines",
                        name="Distribuição Normal",
                        line=dict(color="blue", width=2)
                    ))

                    # Pontos das notas do aluno
                    fig_normal.add_trace(go.Scatter(
                        x=notas_aluno,
                        y=norm.pdf(notas_aluno, mean, std_dev),
                        mode="markers",
                        name="Notas do Aluno",
                        marker=dict(color="red", size=8)
                    ))

                    # Configurações da distribuição normal
                    fig_normal.update_layout(
                        title=f"Distribuição Normal das Notas de {aluno_selecionado}",
                        xaxis_title="Notas",
                        yaxis_title="Densidade",
                        showlegend=True
                    )

                    # Exibir a distribuição normal
                    st.subheader("Distribuição Normal das Notas")
                    st.plotly_chart(fig_normal)
                else:
                    st.warning("O estudante não possui notas registradas.")
            else:
                st.error("Estudante não encontrado. Verifique o número inserido.")

    # Aba 3: Estatísticas da Turma
    with tab3:
        mean_scores = df.drop(columns=["numero", "nome"]).mean()
        st.bar_chart(mean_scores)

    # Aba 4: Ranking de Estudantes
    with tab4:
        df["Media_Geral"] = df.drop(columns=["numero", "nome"]).mean(axis=1)
        ranking = df[["numero", "nome", "Media_Geral"]].sort_values(by="Media_Geral", ascending=False)
        st.dataframe(ranking)

    # Aba 7: Visualização do Banco de Dados
    with tab7:
        st.header("Visualização do Banco de Dados")
        table_name = st.selectbox("Selecione a tabela", ["alunos", "disciplinas", "notas"])
        df_table = load_data(table_name)
        st.dataframe(df_table)