import streamlit as st
import pandas as pd
import numpy as np
from scipy import signal
from io import BytesIO
import matplotlib.pyplot as plt

# 设置页面配置
st.set_page_config(
    page_title="Excel数据降采样工具",
    page_icon="📊",
    layout="wide"
)

# 应用标题和说明
st.title("📊 Excel数据降采样工具")
st.markdown("""
此工具用于对Excel文件中的数据进行降采样处理。  
只需上传您的Excel文件，指定原始频率和目标频率，即可获取降采样后的数据。
**使用说明：**
1. 上传Excel文件（确保第一行为标题，第二行开始为数值）
2. 设置原始采样频率和目标采样频率
3. 查看数据预览和图表
4. 下载处理后的文件
""")

# 文件上传部分
uploaded_file = st.file_uploader(
    "上传Excel文件", 
    type=["xlsx", "xls"],
    help="请确保Excel第一行为标题，第二行开始为数值数据"
)

if uploaded_file is not None:
    try:
        # 读取Excel文件
        df = pd.read_excel(uploaded_file)
        st.success("文件读取成功！")
        
        # 显示文件基本信息
        st.subheader("文件基本信息")
        col1, col2, col3 = st.columns(3)
        col1.metric("总行数", f"{len(df)}")
        col2.metric("总列数", f"{len(df.columns)}")
        col3.metric("数据范围", f"{df.index[0]} - {df.index[-1]}")
        
        # 显示原始数据预览
        with st.expander("查看原始数据预览"):
            st.dataframe(df)
        
        # 频率设置
        st.subheader("降采样参数设置")
        col1, col2 = st.columns(2)
        
        with col1:
            original_freq = st.number_input(
                "原始采样频率 (Hz)", 
                min_value=0.1, 
                max_value=1000.0, 
                value=10.0,
                step=0.1,
                help="例如：10表示原始数据每秒采集10个样本"
            )
        
        with col2:
            target_freq = st.number_input(
                "目标采样频率 (Hz)", 
                min_value=0.1, 
                max_value=1000.0, 
                value=1.0,
                step=0.1,
                help="例如：1表示降采样后每秒保留1个样本"
            )
        
        # 计算降采样比率
        downsample_ratio = int(original_freq / target_freq)
        
        if downsample_ratio <= 1:
            st.warning("目标频率必须小于原始频率才能进行降采样")
        else:
            st.info(f"降采样比率: 每 {downsample_ratio} 个样本保留 1 个样本")
            
            # 执行降采样处理
            st.subheader("降采样处理")
            
            # 创建降采样后的数据框
            downsampled_data = {}
            
            for column in df.columns:
                if df[column].dtype in ['float64', 'int64']:
                    # 对数值列进行降采样
                    data = df[column].values
                    downsampled_data[column] = signal.decimate(data, downsample_ratio)
                else:
                    # 对非数值列进行简单抽样
                    downsampled_data[column] = df[column].iloc[::downsample_ratio].values
            
            # 创建降采样后的DataFrame
            downsampled_df = pd.DataFrame(downsampled_data)
            
            # 显示处理结果
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**原始数据**")
                st.dataframe(df.head(10))
            
            with col2:
                st.markdown("**降采样后的数据**")
                st.dataframe(downsampled_df.head(10))
            
            # 显示数据图表
            st.subheader("数据可视化")
            plot_col = st.selectbox("选择要绘制的列", df.columns)
            
            if df[plot_col].dtype in ['float64', 'int64']:
                fig, ax = plt.subplots(2, 1, figsize=(10, 8))
                
                # 原始数据图表
                ax[0].plot(df[plot_col].values, 'b-', alpha=0.7, label='原始数据')
                ax[0].set_title(f"原始数据 ({len(df)} 个点)")
                ax[0].grid(True)
                ax[0].legend()
                
                # 降采样数据图表
                ax[1].plot(downsampled_df[plot_col].values, 'r-', alpha=0.7, label='降采样数据')
                ax[1].set_title(f"降采样数据 ({len(downsampled_df)} 个点)")
                ax[1].grid(True)
                ax[1].legend()
                
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("选择的列不是数值类型，无法绘制图表")
            
            # 文件下载功能
            st.subheader("下载处理结果")
            
            # 将DataFrame转换为Excel文件
            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='降采样数据')
                processed_data = output.getvalue()
                return processed_data
            
            excel_data = convert_df_to_excel(downsampled_df)
            
            st.download_button(
                label="下载降采样后的Excel文件",
                data=excel_data,
                file_name=f"downsampled_{uploaded_file.name}",
                mime="application/vnd.ms-excel"
            )
    
    except Exception as e:
        st.error(f"处理文件时出错: {str(e)}")
else:
    st.info("请上传Excel文件开始处理")

# 添加页脚
st.markdown("---")
st.markdown("### 使用说明")
st.markdown("""
1. **文件要求**: 确保Excel文件第一行为标题行，第二行开始为数据
2. **频率设置**: 原始频率指数据采集时的频率，目标频率指降采样后的频率
3. **数据处理**: 数值列会使用信号处理算法进行降采样，非数值列会进行简单抽样
4. **结果验证**: 建议始终检查降采样后的数据是否符合预期
""")
