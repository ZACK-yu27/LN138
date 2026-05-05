import random

for i in range(10):
    number = random.randint(1, 100)
    if number % 2 == 0:
        print(f"第{i+1}个数字 {number} 是一个偶数")
    else:
        print(f"第{i+1}个数字 {number} 是一个奇数")