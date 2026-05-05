# 用range()创建一个从1到10的列表
ls = list(range(1, 11))

# 输出列表中的每个元素
for num in ls:
    print(num)
    
# 用列表推导式获取平方
squares = [x**2 for x in ls]

# 计算平方和
sum_squares = sum(squares)

# 输出平方列表和平方和
print("Squares:", squares)
print("Sum of squares:", sum_squares)