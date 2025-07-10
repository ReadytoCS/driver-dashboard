import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import tempfile
import os
import pyperclip

from chart_utils import (
    detect_multi_metric,
    grouped_bar_chart,
    stacked_bar_chart,
    radar_chart,
    suggest_chart_types,
    MCKINSEY_COLORS,
)
from insight_utils import generate_insights

st.set_page_config(
    page_title="ExcelInsight",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        color: #1255b5;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .deck-preview {
        background: #f8f9fa;
        border-radius: 16px;
        width: 1280px;
        height: 720px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 16px rgba(0,0,0,0.04);
        padding: 32px 0;
    }
    .slide-caption {
        color: #888;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    .insight-bullet {
        font-size: 1.25rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📊 ExcelInsight</h1>', unsafe_allow_html=True)
    st.markdown("**Transform your Excel data into interactive charts and professional presentations**")

    deck_preview = st.checkbox("🖥️ Deck Preview Mode", value=False)

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

            cat_col, num_cols = detect_multi_metric(df)
            if cat_col and num_cols:
                st.markdown("### 📊 Multi-Metric Chart Options")
                st.caption("💡 Suggested chart type based on data")
                st.markdown(f"**Detected X (category):** `{cat_col}`")
                st.markdown(f"**Detected Y (metrics):** `{', '.join(num_cols)}`")

                chart_types = suggest_chart_types(df, cat_col, num_cols)
                chart_type = st.selectbox(
                    "Suggested Chart Type",
                    chart_types,
                    help="Choose a chart style to preview.",
                )

                # Chart rendering logic
                if chart_type == "Grouped Bar":
                    fig = grouped_bar_chart(df, cat_col, num_cols)
                elif chart_type == "Stacked Bar":
                    fig = stacked_bar_chart(df, cat_col, num_cols)
                elif chart_type == "Radar":
                    fig = radar_chart(df, cat_col, num_cols)
                elif chart_type == "Pie":
                    fig = px.pie(df, names=cat_col, values=num_cols[0], color_discrete_sequence=MCKINSEY_COLORS)
                elif chart_type == "Treemap":
                    fig = px.treemap(df, path=[cat_col], values=num_cols[0], color_discrete_sequence=MCKINSEY_COLORS)
                else:
                    fig = None

                # Generate insights
                auto_insights = generate_insights(df, cat_col, num_cols)
                if 'edited_insights' not in st.session_state:
                    st.session_state['edited_insights'] = auto_insights.copy()
                # If number of insights changed, reset
                if len(st.session_state['edited_insights']) != len(auto_insights):
                    st.session_state['edited_insights'] = auto_insights.copy()

                # Slide preview mode
                if deck_preview:
                    with st.container():
                        st.markdown('<div class="deck-preview">', unsafe_allow_html=True)
                        st.plotly_chart(fig, use_container_width=False)
                        st.markdown("#### 🔎 Derived Insights", unsafe_allow_html=True)
                        for i, insight in enumerate(auto_insights):
                            edited = st.text_area(f"Edit insight {i+1}", value=st.session_state['edited_insights'][i], key=f"insight_edit_{i}")
                            st.session_state['edited_insights'][i] = edited
                            st.markdown(f"<div class='insight-bullet'>{edited}</div>", unsafe_allow_html=True)
                        st.markdown('<div class="slide-caption">Looks slide-ready?</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.plotly_chart(fig, use_container_width=False)
                    st.markdown("#### 🔎 Derived Insights")
                    for i, insight in enumerate(auto_insights):
                        edited = st.text_area(f"Edit insight {i+1}", value=st.session_state['edited_insights'][i], key=f"insight_edit_{i}")
                        st.session_state['edited_insights'][i] = edited
                        st.markdown(f"- {edited}")

                # Download PNG
                img_bytes = fig.to_image(format="png", width=1100, height=600)
                st.download_button(
                    label="Download PNG",
                    data=img_bytes,
                    file_name=f"{chart_type.replace(' ', '_').lower()}.png",
                    mime="image/png",
                )

                # Copy slide text button
                slide_text = f"{chart_type} for {cat_col} vs {', '.join(num_cols)}\n" + "\n".join(st.session_state['edited_insights'])
                if st.button("Copy Slide Text"):
                    try:
                        pyperclip.copy(slide_text)
                        st.success("Slide text copied to clipboard!")
                    except Exception:
                        st.warning("Copying to clipboard is not supported in this environment.")
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