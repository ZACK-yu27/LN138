#输入长方形数据
data = input("请输入长方形的长和宽(用逗号分隔): ")
length = data.split(",")[0]
width = data.split(",")[1]

#计算长方形面积
area = float(length) * float(width)

#输出结果
print(f"长方形的面积为: {area:.2f}")