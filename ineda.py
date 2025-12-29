# ======================================================================
# 0. Importación de librerías
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# ======================================================================
# Configuración de la página
st.set_page_config(
    page_title="Exploratory Data Analysis App",
    layout="wide"
)

st.title("Exploratory Data Analysis App")

# ======================================================================
# Sidebar - Carga de datos
st.sidebar.header("A) File upload")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV file",
    type=["csv"]
)

# ======================================================================
# Función cacheada para cargar datos
@st.cache_data
def load_data(file):
    return pd.read_csv(file)

if uploaded_file is not None:
    try:
        data = load_data(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        sys.exit()

    # Preprocesamiento ligero
    data.columns = data.columns.str.replace("_", " ").str.title()

    # ==================================================================
    # 1. Vista previa del dataset
    st.subheader("1. Dataset Preview")
    st.dataframe(data, use_container_width=True, hide_index=True)

    st.divider()

    # ==================================================================
    # 2. Exploración del dataset
    st.subheader("2. High-Level Overview")

    option = st.sidebar.radio(
        "B) Data Discovery",
        [
            "Data Dimensions",
            "Field Descriptions",
            "Summary Statistics",
            "Value Counts"
        ]
    )

    if option == "Data Dimensions":
        st.write(f"Rows: {data.shape[0]}")
        st.write(f"Columns: {data.shape[1]}")

    elif option == "Field Descriptions":
        dtypes = (
            data.dtypes
            .reset_index()
            .rename(columns={"index": "Field", 0: "Type"})
        )
        st.dataframe(dtypes, use_container_width=True, hide_index=True)

    elif option == "Summary Statistics":
        stats = data.describe(include="all").round(2)
        nulls = data.isnull().sum().to_frame("Null Count").T
        summary = pd.concat([nulls, stats])
        st.dataframe(summary, use_container_width=True)

    elif option == "Value Counts":
        categorical_cols = data.select_dtypes(include="object").columns
        if len(categorical_cols) == 0:
            st.info("No categorical variables available.")
        else:
            col = st.sidebar.selectbox("Select field", categorical_cols)
            vc = data[col].value_counts().reset_index()
            vc.columns = [col, "Count"]
            st.dataframe(vc, use_container_width=True, hide_index=True)

    st.divider()

    # ==================================================================
    # 3. Visualización
    st.subheader("3. Data Visualization")

    vis = st.sidebar.toggle("C) Enable Visualization")

    if vis:
        numeric_cols = data.select_dtypes(include="number").columns

        if len(numeric_cols) == 0:
            st.warning("No numeric variables available for plotting.")
        else:
            plot_type = st.selectbox(
                "Select plot type",
                ["Histogram", "Boxplot", "Correlation Heatmap"]
            )

            if plot_type == "Histogram":
                col = st.selectbox("Select variable", numeric_cols)
                fig, ax = plt.subplots()
                sns.histplot(data[col], kde=True, ax=ax)
                st.pyplot(fig)

            elif plot_type == "Boxplot":
                col = st.selectbox("Select variable", numeric_cols)
                fig, ax = plt.subplots()
                sns.boxplot(x=data[col], ax=ax)
                st.pyplot(fig)

            elif plot_type == "Correlation Heatmap":
                corr = data[numeric_cols].corr()
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
                st.pyplot(fig)

else:
    st.info("Please upload a CSV file to begin.")
