while True:
    name = input('请输入用户名：')
    if name != 'SYSU':
        print('用户名错误，请重新输入\n')
        continue
    elif name == 'SYSU':      
        password = input('请输入密码：')
        if password != 'Lingnan':
            print('密码错误，请重新输入\n')
            continue
        else:
            print('Access granted.')
            break