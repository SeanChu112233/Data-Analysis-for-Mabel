import os
# 完全禁用 Streamlit 的文件监视器和配置创建
os.environ['STREAMLIT_SERVER_ENABLE_FILE_WATCHER'] = 'false'

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from io import BytesIO
import traceback

# 设置页面标题
st.title('Excel 数据插值热力图生成器')
st.write('上传您的Excel文件，生成插值热力图')

# 添加调试开关
debug_mode = st.sidebar.checkbox("启用调试模式")

# 文件上传区域
uploaded_file = st.file_uploader("选择Excel文件", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        if debug_mode:
            st.write("文件上传成功，开始处理...")
        
        # 读取Excel文件 - 直接在内存中处理，避免文件系统操作
        df = pd.read_excel(uploaded_file)
        
        if debug_mode:
            st.write(f"成功读取Excel文件，形状: {df.shape}")
            st.write(f"列名: {list(df.columns)}")
        
        # 显示数据前几行
        st.subheader('数据预览')
        st.dataframe(df.head())
        
        # 检查数据列数
        if df.shape[1] < 4:
            error_msg = '错误：Excel文件需要至少4列数据（时间、X轴、Y轴、颜色值）'
            st.error(error_msg)
        else:
            # 假设第一列是时间，第二列是X轴，第三列是Y轴，第四列是颜色值
            time_col = df.columns[0]
            x_col = df.columns[1]
            y_col = df.columns[2]
            color_col = df.columns[3]
            
            st.subheader('数据信息')
            st.write(f'时间列: {time_col}')
            st.write(f'X轴列: {x_col}')
            st.write(f'Y轴列: {y_col}')
            st.write(f'颜色值列: {color_col}')
            
            # 检查数据有效性
            if debug_mode:
                st.write(f"X轴数据范围: {df[x_col].min()} 到 {df[x_col].max()}")
                st.write(f"Y轴数据范围: {df[y_col].min()} 到 {df[y_col].max()}")
                st.write(f"颜色值范围: {df[color_col].min()} 到 {df[color_col].max()}")
            
            # 创建插值热力图
            st.subheader('插值热力图')
            
            # 提取数据点
            x = df[x_col].values
            y = df[y_col].values
            z = df[color_col].values
            
            # 检查数据点数量
            if len(x) < 3:
                error_msg = "错误：数据点太少，无法进行插值。至少需要3个数据点。"
                st.error(error_msg)
                st.stop()
            
            # 创建网格
            xi = np.linspace(min(x), max(x), 100)
            yi = np.linspace(min(y), max(y), 100)
            XI, YI = np.meshgrid(xi, yi)
            
            if debug_mode:
                st.write(f"创建网格: {XI.shape}")
            
            # 使用线性插值方法
            try:
                ZI = griddata((x, y), z, (XI, YI), method='linear')
                
                if debug_mode:
                    st.write(f"插值完成，结果形状: {ZI.shape}")
                
                # 检查插值结果
                if np.isnan(ZI).all():
                    error_msg = "插值失败：无法从数据点生成表面。请检查数据分布。"
                    st.error(error_msg)
                    st.stop()
                
            except Exception as e:
                error_msg = f"插值过程中出错: {str(e)}"
                st.error(error_msg)
                if debug_mode:
                    st.write(traceback.format_exc())
                st.stop()
            
            # 创建自定义颜色映射（从深蓝到深红，中间经过绿色和黄色）
            colors = ['darkblue', 'blue', 'lightblue', 'green', 'yellow', 'orange', 'red', 'darkred']
            positions = [0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
            
            # 创建自定义颜色映射
            from matplotlib.colors import LinearSegmentedColormap
            custom_cmap = LinearSegmentedColormap.from_list("custom", list(zip(positions, colors)))
            
            # 创建图形
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 绘制插值热力图
            try:
                contour = ax.contourf(XI, YI, ZI, 100, cmap=custom_cmap, alpha=0.8)
                
                # 添加原始数据点（可选）
                scatter = ax.scatter(x, y, c=z, cmap=custom_cmap, edgecolors='black', linewidth=0.5, s=30)
                
                # 添加颜色条
                cbar = plt.colorbar(contour)
                cbar.set_label(color_col, fontsize=12)
                
                # 设置标题和标签
                ax.set_xlabel(x_col, fontsize=12)
                ax.set_ylabel(y_col, fontsize=12)
                ax.set_title(f'{color_col} 插值热力图', fontsize=14)
                
                # 显示图形
                st.pyplot(fig)
                
                # 提供下载选项
                st.subheader('下载热力图')
                buf = BytesIO()
                fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
                buf.seek(0)
                
                st.download_button(
                    label="下载热力图",
                    data=buf,
                    file_name="interpolated_heatmap.png",
                    mime="image/png"
                )
                
                if debug_mode:
                    st.write("热力图生成成功")
                
            except Exception as e:
                error_msg = f"绘图过程中出错: {str(e)}"
                st.error(error_msg)
                if debug_mode:
                    st.write(traceback.format_exc())
            
            # 显示插值方法说明
            st.sidebar.subheader("插值说明")
            st.sidebar.info("""
            此热力图使用线性插值方法从离散数据点生成连续表面。
            
            插值方法：
            - 网格分辨率：100x100
            - 插值算法：线性插值
            - 原始数据点显示为散点
            
            如果数据点分布不均匀，插值结果可能不够精确。
            """)
            
    except Exception as e:
        error_msg = f"处理文件时出错: {str(e)}"
        st.error(error_msg)
        if debug_mode:
            st.write(traceback.format_exc())
        st.error("请确保Excel文件格式正确，且包含足够的数据点进行插值。")
else:
    st.info('请上传Excel文件以继续')

# 添加使用说明
st.sidebar.title('使用说明')
st.sidebar.markdown("""
1. 准备Excel文件，确保包含至少4列数据：
   - 第一列：时间数据
   - 第二列：X轴数据
   - 第三列：Y轴数据
   - 第四列：颜色值数据（0-100之间的值，如转化率)

2. 点击"选择Excel文件"按钮上传文件

3. 应用会自动检测各列并生成插值热力图

4. 您可以使用"下载热力图"按钮保存图像

**注意**：插值热力图需要足够的数据点才能生成准确的结果。
如果数据点太少或分布不均匀，插值结果可能不够精确。
""")

# 添加调试信息
if debug_mode:
    st.sidebar.subheader("调试信息")
    st.sidebar.write("Streamlit版本:", st.__version__)
    st.sidebar.write("Pandas版本:", pd.__version__)
    st.sidebar.write("NumPy版本:", np.__version__)
    try:
        import scipy
        st.sidebar.write("SciPy版本:", scipy.__version__)
    except:
        st.sidebar.write("SciPy未安装")
