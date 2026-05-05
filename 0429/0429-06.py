while True:
    num1 = input("请输入第一个数：")
    if num1 == 'quit':
        print("程序结束")
        break

    num2 = input("请输入第二个数：")
    if num2 == 'quit':
        print("程序结束")
        break

    try:
        n1 = float(num1)
        n2 = float(num2)

        if n2 == 0:
            print("除数不能为0！")
        else:
            result = n1 / n2
            print(f"商为：{result}")
    except ValueError:
        print("输入的数据有误！")

    print("本次计算结束")
