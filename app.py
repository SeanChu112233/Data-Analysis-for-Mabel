import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="CSV降采样工具", page_icon="📊", layout="wide")

st.title("📊 CSV文件降采样处理工具")
st.markdown("""
欢迎使用CSV降采样工具！本工具允许您上传CSV文件，并对数据进行降低采样频率处理。
只需上传文件，设置原始和目标采样率，即可获取处理后的数据。
""")

# 文件上传区域
st.header("1. 文件上传")
uploaded_file = st.file_uploader("上传CSV文件", type=["csv"], 
                                 help="请确保CSV文件第一行为标题行，第二行开始是数值数据")

if uploaded_file is not None:
    try:
        # 读取CSV文件
        df = pd.read_csv(uploaded_file)
        
        # 显示文件基本信息
        st.success(f"文件上传成功！数据集形状: {df.shape[0]}行 × {df.shape[1]}列")
        
        # 创建双列布局
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("数据预览")
            st.dataframe(df.head(10), use_container_width=True)
        
        with col2:
            st.subheader("数据信息")
            st.markdown(f"""
            - **总行数**: {df.shape[0]}
            - **总列数**: {df.shape[1]}
            - **列名**: {', '.join(list(df.columns))}
            """)
        
        # 降采样设置
        st.header("2. 降采样设置")
        st.markdown("设置原始采样率和目标采样率以进行降采样处理")
        
        samp_col1, samp_col2, samp_col3 = st.columns(3)
        
        with samp_col1:
            original_rate = st.number_input("原始采样率 (Hz)", min_value=0.1, 
                                           value=10.0, step=1.0,
                                           help="例如: 数据采集时的采样频率为10Hz")
        
        with samp_col2:
            target_rate = st.number_input("目标采样率 (Hz)", min_value=0.1, 
                                         value=1.0, step=0.1,
                                         help="例如: 降低到1Hz")
        
        with samp_col3:
            # 计算降采样系数
            downsample_factor = int(original_rate / target_rate)
            st.metric("降采样系数", f"{downsample_factor}:1")
            st.caption(f"即每{downsample_factor}个样本保留1个")
        
        # 执行降采样
        st.header("3. 执行降采样")
        if st.button("执行降采样处理", type="primary"):
            if original_rate <= target_rate:
                st.error("目标采样率必须小于原始采样率！")
            else:
                with st.spinner("正在处理数据..."):
                    # 执行降采样
                    downsampled_df = df.iloc[::downsample_factor, :].reset_index(drop=True)
                    
                    # 显示结果
                    st.success(f"降采样完成！处理后的数据集形状: {downsampled_df.shape[0]}行 × {downsampled_df.shape[1]}列")
                    
                    # 创建双选项卡显示结果
                    tab1, tab2 = st.tabs(["处理结果", "数据统计"])
                    
                    with tab1:
                        st.dataframe(downsampled_df, use_container_width=True)
                        
                        # 提供下载链接
                        csv_data = downsampled_df.to_csv(index=False)
                        st.download_button(
                            label="下载处理后的CSV文件",
                            data=csv_data,
                            file_name="downsampled_data.csv",
                            mime="text/csv"
                        )
                    
                    with tab2:
                        st.markdown("**原始数据统计**")
                        st.dataframe(df.describe(), use_container_width=True)
                        
                        st.markdown("**降采样后数据统计**")
                        st.dataframe(downsampled_df.describe(), use_container_width=True)
                    
                    # 简单可视化
                    st.subheader("数据可视化")
                    numeric_columns = downsampled_df.select_dtypes(include=[np.number]).columns
                    
                    if len(numeric_columns) > 0:
                        selected_column = st.selectbox("选择要可视化的数值列", numeric_columns)
                        
                        if selected_column:
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.markdown("**原始数据**")
                                st.line_chart(df[selected_column])
                            
                            with col_b:
                                st.markdown("**降采样后数据**")
                                st.line_chart(downsampled_df[selected_column])
                    else:
                        st.info("未检测到数值型列进行可视化")
    
    except Exception as e:
        st.error(f"处理文件时出错: {str(e)}")
else:
    st.info("👆 请上传CSV文件开始处理")

# 添加使用说明
with st.expander("使用说明"):
    st.markdown("""
    ### 使用步骤:
    1.  **上传文件**: 点击"上传CSV文件"按钮，选择您的CSV文件
    2.  **设置参数**: 
        - 设置正确的**原始采样率**（您的数据采集频率）
        - 设置**目标采样率**（您希望降低到的频率）
    3.  **执行处理**: 点击"执行降采样处理"按钮
    4.  **查看结果**: 在选项卡中查看处理后的数据和统计信息
    5.  **下载结果**: 点击"下载处理后的CSV文件"按钮保存结果
    
    ### 注意事项:
    - 确保CSV文件第一行为标题行
    - 确保从第二行开始是数值数据
    - 目标采样率必须小于原始采样率
    - 系统会自动计算降采样系数（整数）
    """)

# 添加页脚
st.markdown("---")
st.markdown("📊 *CSV降采样工具 | 让数据处理更高效*")
