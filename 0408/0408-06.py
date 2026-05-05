#让用户一次性输入长宽高
length, width, height = map(float, input("请输入长宽高，以英文逗号分隔: ").split(","))
volume = length * width * height
print(f"长方体的体积为: {volume}")