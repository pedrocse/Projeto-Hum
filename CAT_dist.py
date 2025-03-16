import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurações iniciais do Streamlit
st.set_page_config(page_title="Visualizador de Pontuação", layout="wide")
st.title("📊 Visualizador de Pontuação de Grupo")

# Função para carregar o arquivo Excel
def load_data(uploaded_file, sheet_name):
    try:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=["xlsx"])

    if uploaded_file:
        # Listar as planilhas disponíveis no arquivo Excel
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        selected_sheet = st.selectbox("Selecione a planilha:", sheet_names)

        # Carregar os dados
        if st.button("Carregar Dados"):
            df = load_data(uploaded_file, selected_sheet)
            if df is not None:
                st.session_state.df = df
                st.success(f"Dados carregados com sucesso da planilha '{selected_sheet}'!")

# Verificar se os dados foram carregados
if "df" in st.session_state:
    df = st.session_state.df

    # Exibir os dados carregados
    st.subheader("📋 Dados Carregados")
    st.dataframe(df)

    # Selecionar colunas para plotagem
    st.subheader("📊 Gerar Gráficos")
    columns = df.columns.tolist()
    x_axis = st.selectbox("Selecione a coluna para o Eixo X:", columns)
    y_axis = st.multiselect("Selecione a(s) coluna(s) para o Eixo Y:", columns)

    if x_axis and y_axis:
        chart_type = st.selectbox("Selecione o tipo de gráfico:",
                                  ["Gráfico de Barras", "Gráfico de Linhas", "Gráfico de Dispersão"])

        # Gerar o gráfico
        if st.button("Gerar Gráfico"):
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "Gráfico de Barras":
                for col in y_axis:
                    sns.barplot(data=df, x=x_axis, y=col, ax=ax, label=col)
                ax.set_title("Gráfico de Distribuição de Notas do CAT")
                ax.legend()

            elif chart_type == "Gráfico de Linhas":
                for col in y_axis:
                    sns.lineplot(data=df, x=x_axis, y=col, ax=ax, label=col)
                ax.set_title("Gráfico de Linhas")
                ax.legend()

            elif chart_type == "Gráfico de Dispersão":
                for col in y_axis:
                    sns.scatterplot(data=df, x=x_axis, y=col, ax=ax, label=col)
                ax.set_title("Gráfico de Dispersão")
                ax.legend()

            # Melhorias para evitar sobreposição no eixo X
            plt.xticks(rotation=45, ha='right')  # Rotaciona os rótulos do eixo X em 45 graus
            plt.tight_layout()  # Ajusta o layout para evitar cortes

            # Exibir o gráfico
            st.pyplot(fig)

else:
    st.info("Por favor, carregue um arquivo Excel para começar.")