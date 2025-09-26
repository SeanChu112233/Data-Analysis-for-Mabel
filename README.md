# 团队贡献数据分析工具

这是一个使用Streamlit开发的数据分析小程序，用于分析温度(temp)、时间(time)与推出力(force)之间的关系。该工具支持多种回归模型，并提供直观的可视化结果，方便团队成员共同分析和决策。

## 功能特点

- 支持上传包含temp、time、force数据的CSV文件
- 提供四种回归模型进行数据分析：线性回归、多项式回归、随机森林、梯度提升树
- 自动评估各模型性能并推荐最佳模型
- 提供3D关系图、热区图等多种可视化方式
- 支持交互式参数调整和结果预测
- 分析各参数对结果的影响程度

## 数据格式要求

CSV文件应满足以下格式：
- 第一行为参数名称：包含temp（温度）、time（时间）、force（推出力）
- 从第二行开始为数据，每个参数各占一列
- 示例：
  ```
  temp,time,force
  70,60,3.4
  70,180,3.1
  70,300,3.3
  90,60,3.1
  ```

## 安装与使用

1. 克隆本仓库到本地
   ```
   git clone https://github.com/你的用户名/team-contribution-analyzer.git
   cd team-contribution-analyzer
   ```

2. 安装所需依赖
   ```
   pip install -r requirements.txt
   ```

3. 运行程序
   ```
   streamlit run app.py
   ```

4. 在浏览器中打开显示的本地地址（通常是http://localhost:8501）

5. 上传你的CSV数据文件开始分析

## 依赖项

- streamlit
- numpy
- pandas
- matplotlib
- seaborn
- scikit-learn
- plotly

所有依赖项已列在requirements.txt文件中。

## 团队协作

欢迎团队成员贡献代码或提出改进建议：
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request
    
