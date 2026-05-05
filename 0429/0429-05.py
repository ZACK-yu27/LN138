while True:
    name = input("请输入用户名：")

    is_all_alpha = name.isalpha()
    if not is_all_alpha:
        print("用户名必须全是字符")
        continue

    if name != 'SYSU':
        continue

    while True:
        password = input("请输入密码：")

        if password != 'Lingnan':
            continue

        print("Access granted.")
        break
    break
