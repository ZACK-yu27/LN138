# 定义年份列表，从2011到2025
year = list(range(2011, 2026))

# 定义GDP列表
gdp = [48.9, 54, 59.5, 64.4, 68.9, 74.4, 82.7, 90, 99.09, 101.6, 114.92, 121.02, 126.06, 134.9, 140.2]

# 计算年均GDP
average_gdp = sum(gdp) / len(gdp)

# 格式化输出年均GDP
print(f"年均GDP为：{average_gdp:.2f}万亿元")

# 添加图形绘制代码
import matplotlib.pyplot as plt  # 导入pyplot库
# 1. 设置中文字体：Windows用SimHei(黑体)，Mac/Linux看下方替换
plt.rcParams['font.sans-serif'] = ['SimHei']
# 2. 解决负号 - 显示成方框的问题
plt.rcParams['axes.unicode_minus'] = False
plt.plot(year, gdp, 'b-', linewidth=2)  # 画线型图
plt.title('年度GDP变化趋势图')
plt.xlabel('年份')  # 横轴名称
plt.ylabel('GDP（万亿元）')  # 纵轴名称
plt.show()  # 显示图形