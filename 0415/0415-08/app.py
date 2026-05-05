import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import time
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="DataExplorer - 交互式数据探索工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

if 'data' not in st.session_state:
    st.session_state.data = None
if 'file_info' not in st.session_state:
    st.session_state.file_info = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False


def validate_file(uploaded_file):
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_name = uploaded_file.name.lower()
    for ext in allowed_extensions:
        if file_name.endswith(ext):
            return True, ext
    return False, None


def load_data(uploaded_file):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("正在验证文件格式...")
    progress_bar.progress(10)
    time.sleep(0.3)
    
    is_valid, ext = validate_file(uploaded_file)
    if not is_valid:
        progress_bar.empty()
        status_text.empty()
        return None, "不支持的文件格式。请上传 .xlsx, .xls 或 .csv 文件。"
    
    status_text.text("正在读取数据...")
    progress_bar.progress(30)
    time.sleep(0.3)
    
    try:
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(uploaded_file, engine='openpyxl' if ext == '.xlsx' else 'xlrd')
        else:
            df = pd.read_csv(uploaded_file)
        
        progress_bar.progress(70)
        time.sleep(0.3)
        
        status_text.text("正在处理数据...")
        progress_bar.progress(90)
        time.sleep(0.3)
        
        file_size = uploaded_file.size
        progress_bar.progress(100)
        time.sleep(0.3)
        
        progress_bar.empty()
        status_text.empty()
        
        return df, None
        
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        return None, f"文件读取失败: {str(e)}"


def show_file_upload():
    st.title("📊 DataExplorer - 交互式数据探索工具")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📁 上传数据文件")
        st.markdown("支持格式: **.xlsx**, **.xls**, **.csv**")
        st.markdown("最大文件大小: **200MB**")
        st.markdown("建议支持至少 **10万行** 数据分析")
    
    uploaded_file = st.file_uploader(
        "选择文件",
        type=['xlsx', 'xls', 'csv'],
        help="上传Excel或CSV文件进行数据分析"
    )
    
    if uploaded_file is not None:
        with st.spinner("正在处理文件..."):
            df, error = load_data(uploaded_file)
        
        if error:
            st.error(f"❌ {error}")
        else:
            st.session_state.data = df
            st.session_state.file_info = {
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'type': uploaded_file.type
            }
            st.session_state.analysis_complete = True
            st.success(f"✅ 文件上传成功！已加载 {df.shape[0]} 行 × {df.shape[1]} 列 数据")
            st.rerun()


def show_data_overview():
    df = st.session_state.data
    
    st.header("📋 数据概览")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总行数", f"{df.shape[0]:,}")
    with col2:
        st.metric("总列数", f"{df.shape[1]}")
    with col3:
        memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("内存占用", f"{memory_mb:.2f} MB")
    with col4:
        file_info = st.session_state.file_info
        if file_info:
            size_kb = file_info['size'] / 1024
            st.metric("文件大小", f"{size_kb:.2f} KB")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("数据类型分布")
        dtype_counts = df.dtypes.astype(str).value_counts()
        
        dtype_df = pd.DataFrame({
            '数据类型': dtype_counts.index,
            '数量': dtype_counts.values
        })
        st.dataframe(dtype_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("列信息")
        col_info = pd.DataFrame({
            '列名': df.columns,
            '数据类型': df.dtypes.astype(str).values,
            '非空数量': df.count().values
        })
        st.dataframe(col_info, hide_index=True, use_container_width=True)


def show_data_preview():
    df = st.session_state.data
    
    st.header("👀 数据预览")
    st.markdown("显示数据集的前10行记录")
    
    st.dataframe(df.head(10), use_container_width=True)
    
    with st.expander("📜 查看更多数据信息"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**列名列表:**")
            st.code(", ".join(df.columns))
        with col2:
            st.write("**数据类型详情:**")
            dtype_details = df.dtypes.apply(lambda x: str(x))
            for col, dtype in dtype_details.items():
                st.write(f"- {col}: {dtype}")


def show_missing_values():
    df = st.session_state.data
    
    st.header("❌ 缺失值分析")
    
    missing_stats = pd.DataFrame({
        '列名': df.columns,
        '缺失数量': df.isnull().sum().values,
        '缺失比例(%)': (df.isnull().sum() / len(df) * 100).round(2).values,
        '数据类型': df.dtypes.astype(str).values
    })
    
    missing_stats = missing_stats.sort_values('缺失数量', ascending=False)
    
    st.subheader("缺失值统计表")
    st.dataframe(missing_stats, hide_index=True, use_container_width=True)
    
    total_missing = df.isnull().sum().sum()
    total_cells = df.shape[0] * df.shape[1]
    missing_pct = total_missing / total_cells * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总缺失值", f"{total_missing:,}")
    with col2:
        st.metric("总缺失比例", f"{missing_pct:.2f}%")
    
    st.markdown("---")
    st.subheader("📉 缺失值热力图")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    missing_matrix = df.isnull().astype(int)
    im = ax.imshow(missing_matrix, cmap='RdYlGn_r', aspect='auto', interpolation='nearest')
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('缺失状态 (0=非缺失, 1=缺失)', fontsize=10)
    
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=45, ha='right', fontsize=9)
    ax.set_yticks([])
    ax.set_xlabel('列名', fontsize=12)
    ax.set_ylabel('行索引', fontsize=12)
    ax.set_title('缺失值热力图 (红色=缺失, 绿色=非缺失)', fontsize=14)
    
    st.pyplot(fig)


def show_descriptive_stats():
    df = st.session_state.data
    
    st.header("📈 描述性统计分析")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if numeric_cols:
        st.subheader("数值型特征统计")
        
        desc_stats = df[numeric_cols].describe().T
        desc_stats = desc_stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        desc_stats.columns = ['计数', '均值', '标准差', '最小值', '25%分位', '中位数', '75%分位', '最大值']
        
        st.dataframe(desc_stats.style.format("{:.4f}"), use_container_width=True)
    else:
        st.info("数据集中没有数值型特征")


def show_correlation():
    df = st.session_state.data
    
    st.header("🔗 特征相关性分析")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("数值型特征少于2个，无法计算相关性")
        return
    
    corr_matrix = df[numeric_cols].corr()
    
    st.subheader("相关系数矩阵")
    st.dataframe(corr_matrix.style.format("{:.4f}").background_gradient(cmap='RdBu_r', axis=None), 
                 use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 相关性热力图")
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    im = ax.imshow(corr_matrix.values, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('相关系数', fontsize=10)
    
    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_yticks(range(len(corr_matrix.columns)))
    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(corr_matrix.columns, fontsize=9)
    
    for i in range(len(corr_matrix.columns)):
        for j in range(len(corr_matrix.columns)):
            text = ax.text(j, i, f'{corr_matrix.values[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title('特征相关性热力图', fontsize=16, pad=20)
    
    st.pyplot(fig)


def show_numeric_distribution():
    df = st.session_state.data
    
    st.header("📊 数值型特征分布分析")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not numeric_cols:
        st.warning("数据集中没有数值型特征")
        return
    
    selected_col = st.selectbox("选择特征", numeric_cols, key="numeric_dist")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("直方图")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(df[selected_col].dropna(), bins=30, edgecolor='black', alpha=0.7, color='#00CC96')
        ax.set_xlabel(selected_col, fontsize=12)
        ax.set_ylabel('频数', fontsize=12)
        ax.set_title(f'{selected_col} 直方图', fontsize=14)
        ax.grid(axis='y', alpha=0.3)
        st.pyplot(fig)
    
    with col2:
        st.subheader("核密度估计图 (KDE)")
        fig, ax = plt.subplots(figsize=(8, 5))
        df[selected_col].dropna().plot(kind='kde', ax=ax, color='#636EFA', linewidth=2)
        ax.set_xlabel(selected_col, fontsize=12)
        ax.set_ylabel('密度', fontsize=12)
        ax.set_title(f'{selected_col} 核密度估计图', fontsize=14)
        ax.grid(axis='both', alpha=0.3)
        st.pyplot(fig)
    
    st.markdown("---")
    st.subheader("所有数值型特征分布")
    
    cols_per_row = 3
    rows = (len(numeric_cols) + cols_per_row - 1) // cols_per_row
    
    fig, axes = plt.subplots(rows, cols_per_row, figsize=(15, 4*rows))
    axes = axes.flatten() if len(numeric_cols) > 1 else [axes]
    
    for i, col in enumerate(numeric_cols):
        axes[i].hist(df[col].dropna(), bins=30, edgecolor='black', alpha=0.7, color='#00CC96')
        axes[i].set_title(f'{col}', fontsize=10)
        axes[i].set_xlabel('')
        axes[i].grid(axis='y', alpha=0.3)
    
    for j in range(len(numeric_cols), len(axes)):
        axes[j].axis('off')
    
    plt.tight_layout()
    st.pyplot(fig)


def show_categorical_distribution():
    df = st.session_state.data
    
    st.header("📊 分类型特征分布分析")
    
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if not cat_cols:
        st.info("数据集中没有分类型特征")
        return
    
    selected_col = st.selectbox("选择特征", cat_cols, key="cat_dist")
    
    freq_table = df[selected_col].value_counts().reset_index()
    freq_table.columns = [selected_col, '频数']
    freq_table['比例(%)'] = (freq_table['频数'] / len(df) * 100).round(2)
    
    st.subheader("频数分布表")
    st.dataframe(freq_table, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.subheader("条形图")
    
    top_n = 20
    if len(freq_table) > top_n:
        plot_data = freq_table.head(top_n)
        title_suffix = f" (前{top_n}类)"
    else:
        plot_data = freq_table
        title_suffix = ""
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bars = ax.barh(plot_data[selected_col], plot_data['频数'], color='#AB63FA', edgecolor='black', alpha=0.8)
    ax.set_xlabel('频数', fontsize=12)
    ax.set_ylabel(selected_col, fontsize=12)
    ax.set_title(f'{selected_col} 频数分布{title_suffix}', fontsize=14)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    for bar, count in zip(bars, plot_data['频数']):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{count:,}', va='center', fontsize=9)
    
    st.pyplot(fig)
    
    st.markdown("---")
    st.subheader("所有分类型特征分布")
    
    for col in cat_cols[:5]:
        with st.expander(f"📊 {col}"):
            freq = df[col].value_counts().head(10)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(freq.index, freq.values, color='#AB63FA', alpha=0.8)
            ax.set_xlabel('频数')
            ax.set_title(f'{col}')
            ax.invert_yaxis()
            st.pyplot(fig)


def show_groupby_analysis():
    df = st.session_state.data
    
    st.header("🔧 分组统计 (GroupBy)")
    
    all_cols = df.columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        groupby_col = st.selectbox("选择分组字段", all_cols, key="gb_col")
    
    with col2:
        agg_cols = st.multiselect("选择聚合列", all_cols, default=all_cols[:1] if all_cols else [], key="gb_agg")
    
    with col3:
        agg_funcs = st.multiselect("选择聚合方式", 
                                    ['sum', 'mean', 'count', 'min', 'max', 'std', 'median'],
                                    default=['mean'], key="gb_func")
    
    if agg_cols and agg_funcs:
        try:
            result = df.groupby(groupby_col)[agg_cols].agg(agg_funcs)
            
            st.subheader("分组统计结果")
            st.dataframe(result, use_container_width=True)
            
            with st.expander("导出结果"):
                csv = result.to_csv()
                st.download_button(
                    label="下载为CSV",
                    data=csv,
                    file_name="groupby_result.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"分组统计失败: {str(e)}")
    else:
        st.info("请选择至少一个聚合列和聚合方式")


def show_pivot_table():
    df = st.session_state.data
    
    st.header("🔧 透视表分析 (Pivot Table)")
    
    all_cols = df.columns.tolist()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        index_col = st.selectbox("选择行索引", all_cols, key="pt_idx")
    
    with col2:
        columns_col = st.selectbox("选择列", all_cols, key="pt_col")
    
    with col3:
        values_col = st.selectbox("选择值字段", all_cols, key="pt_val")
    
    with col4:
        aggfunc = st.selectbox("聚合方式", ['mean', 'sum', 'count', 'min', 'max', 'std'], key="pt_agg")
    
    try:
        pivot = pd.pivot_table(
            df,
            index=index_col,
            columns=columns_col,
            values=values_col,
            aggfunc=aggfunc,
            fill_value=0
        )
        
        st.subheader("透视表结果")
        st.dataframe(pivot.style.format("{:.2f}"), use_container_width=True)
        
        st.markdown("---")
        st.subheader("透视表热力图")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        top_pivot = pivot.head(20)
        
        im = ax.imshow(top_pivot.values, cmap='YlOrRd', aspect='auto')
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('值', fontsize=10)
        
        ax.set_xticks(range(len(top_pivot.columns)))
        ax.set_yticks(range(len(top_pivot.index)))
        ax.set_xticklabels(top_pivot.columns, rotation=45, ha='right', fontsize=9)
        ax.set_yticklabels(top_pivot.index, fontsize=9)
        
        for i in range(len(top_pivot.index)):
            for j in range(len(top_pivot.columns)):
                val = top_pivot.values[i, j]
                text_color = "white" if val > (top_pivot.values.max() + top_pivot.values.min()) / 2 else "black"
                ax.text(j, i, f'{val:.2f}', ha="center", va="center", color=text_color, fontsize=8)
        
        ax.set_title(f'透视表热力图 ({aggfunc})', fontsize=14)
        
        st.pyplot(fig)
        
        with st.expander("导出透视表"):
            csv = pivot.to_csv()
            st.download_button(
                label="下载为CSV",
                data=csv,
                file_name="pivot_table.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"透视表生成失败: {str(e)}")


def main():
    if st.session_state.data is None:
        show_file_upload()
    else:
        st.set_page_config(
            page_title="DataExplorer - 数据分析",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        with st.sidebar:
            st.title("📊 DataExplorer")
            st.markdown("---")
            
            menu_options = [
                "📋 数据概览",
                "👀 数据预览",
                "❌ 缺失值分析",
                "📈 描述性统计",
                "🔗 相关性分析",
                "📊 数值分布",
                "📊 分类分布",
                "🔧 分组统计",
                "🔧 透视表"
            ]
            
            selected = st.radio("功能菜单", menu_options)
            
            st.markdown("---")
            
            if st.button("🔄 上传新文件", use_container_width=True):
                st.session_state.data = None
                st.session_state.file_info = None
                st.session_state.analysis_complete = False
                st.rerun()
            
            file_info = st.session_state.file_info
            if file_info:
                st.markdown("---")
                st.caption("当前文件:")
                st.caption(f"**{file_info['name']}**")
                size_kb = file_info['size'] / 1024
                st.caption(f"大小: {size_kb:.2f} KB")
        
        if selected == "📋 数据概览":
            show_data_overview()
        elif selected == "👀 数据预览":
            show_data_preview()
        elif selected == "❌ 缺失值分析":
            show_missing_values()
        elif selected == "📈 描述性统计":
            show_descriptive_stats()
        elif selected == "🔗 相关性分析":
            show_correlation()
        elif selected == "📊 数值分布":
            show_numeric_distribution()
        elif selected == "📊 分类分布":
            show_categorical_distribution()
        elif selected == "🔧 分组统计":
            show_groupby_analysis()
        elif selected == "🔧 透视表":
            show_pivot_table()


if __name__ == "__main__":
    main()