while True:
    age = input('请输入年龄（若要退出输入“eixt”）：')
    price = None
    if age == 'exit':
        break
    elif int(age) < 4:
        price = 0
    elif int(age) < 18 and int(age) >= 65:
        price = 5
    else:
        price = 10
    print(f'票价为{price}元')
    continue
