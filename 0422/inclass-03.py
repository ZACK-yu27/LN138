num = eval(input('请输入一个非负整数：'))

while True:
    if type(num) != int:
        print('这不是一个整数')
        num = eval(input('请重新输入一个非负整数：'))
        continue
    elif num < 0:
        print('这不是一个非负数')
        num = eval(input('请重新输入一个非负整数：'))
        continue
    for i in range(int(num ** 0.5) +1):
        if num % i == 0:
            print('这是一个素数')
            break
