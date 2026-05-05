# 第一步：导入Python内置的keyword模块
import keyword

# 第二步：打印所有Python关键字列表
print("Python所有关键字：")
print(keyword.kwlist)

# 可选：格式化输出，让关键字一行一个，更易读
print("\n格式化后的关键字列表：")
for idx, kw in enumerate(keyword.kwlist, 1):
    print(f"{idx}. {kw}")