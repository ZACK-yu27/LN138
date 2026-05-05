while True:
    user_input = input("请输入一个整数（输入quit退出）：")

    if user_input == 'quit':
        print("程序结束")
        break

    try:
        num = int(user_input)

        if num < 2:
            is_prime = False
        else:
            is_prime = True
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break

        if is_prime:
            print(f"{num} 是素数")
        else:
            print(f"{num} 不是素数")
    except ValueError:
        print("输入错误")
