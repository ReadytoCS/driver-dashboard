import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import tempfile
import os

# Import only the new multi-metric chart utilities
from chart_utils import (
    detect_multi_metric,
    grouped_bar_chart,
    stacked_bar_chart,
    radar_chart,
    generate_insights,
)

# Page configuration
st.set_page_config(
    page_title="ExcelInsight",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
st.markdown("""
<style>
    .main-header {
        color: #1255b5;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #1255b5;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #0d4a8f;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 ExcelInsight</h1>', unsafe_allow_html=True)
    st.markdown("**Transform your Excel data into interactive charts and professional presentations**")
    
    # File upload section
    st.markdown("### 📁 Upload Excel File")
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xls or .xlsx)",
        type=['xls', 'xlsx'],
        help="Maximum file size: 20 MB"
    )
    
    if uploaded_file is not None:
        file_size = len(uploaded_file.getvalue())
        if file_size > 20 * 1024 * 1024:
            st.error("❌ File size exceeds 20 MB limit. Please upload a smaller file.")
            return
        try:
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            if not sheet_names:
                st.error("❌ No sheets found in the Excel file.")
                return
            st.success(f"✅ File uploaded successfully! Found {len(sheet_names)} sheet(s).")
            st.markdown("### 📋 Select Sheet")
            selected_sheet = st.selectbox(
                "Choose a sheet to analyze:",
                sheet_names,
                index=0
            )
            with st.spinner("Loading data..."):
                try:
                    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
                except Exception as e:
                    st.error(f"❌ Error loading sheet '{selected_sheet}': {str(e)}")
                    return
            st.markdown("### 📊 Data Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            st.markdown("#### Preview of Data")
            st.dataframe(df.head(10), use_container_width=True)

            # --- Multi-Metric Chart Section ---
            cat_col, num_cols = detect_multi_metric(df)
            if cat_col and num_cols:
                st.markdown("### 📊 Multi-Metric Chart Options")
                st.caption("💡 Suggested chart type based on data")
                st.markdown(f"**Detected X (category):** `{cat_col}`")
                st.markdown(f"**Detected Y (metrics):** `{', '.join(num_cols)}`")
                chart_type = st.selectbox(
                    "Chart type",
                    ["Grouped Bar", "Stacked Bar", "Radar"],
                    help="Suggested based on your data structure.",
                )
                if chart_type == "Grouped Bar":
                    fig = grouped_bar_chart(df, cat_col, num_cols)
                elif chart_type == "Stacked Bar":
                    fig = stacked_bar_chart(df, cat_col, num_cols)
                else:
                    fig = radar_chart(df, cat_col, num_cols)
                st.plotly_chart(fig, use_container_width=False)
                img_bytes = fig.to_image(format="png", width=1100, height=600)
                st.download_button(
                    label="Download PNG",
                    data=img_bytes,
                    file_name=f"{chart_type.replace(' ', '_').lower()}.png",
                    mime="image/png",
                )
                st.markdown("#### 🔎 Derived Insights")
                for insight in generate_insights(df, cat_col, num_cols):
                    st.markdown(insight)
            else:
                st.warning("⚠️ No suitable multi-metric chart pattern detected. Try uploading a file with one categorical and multiple numeric columns.")
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    else:
        st.markdown("""
        ### 🚀 How to Use ExcelInsight
        1. **Upload** your Excel file (.xls or .xlsx) - max 20 MB
        2. **Select** a sheet to analyze
        3. **Review** auto-detected charts or choose chart type
        4. **Download** charts as PNG
        ---
        **Supported Chart Types:**
        - 📊 **Multi-Metric Charts**: One categorical + multiple numeric columns
          - Grouped Bar Charts
          - Stacked Bar Charts
          - Radar Charts
        """)

if __name__ == "__main__":
    main() 