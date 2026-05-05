a, b, c = eval(input("请输入系数a，b，c："))

#计算公式
result = (-b - (pow(b, 2) - 4 * a * c) ** 0.5) / (2 * a)

print(f"结果为{result}")