while True:
    salary = input('请输入月薪（输入“q”退出）：')
    if salary == 'q':
        break
    salary = float(salary)
    if salary < 0:
        print('输入有误，请重新输入')
        continue
    slry_for_tax = salary - 3500
    tax = None
    if slry_for_tax <= 0:
        tax = 0
    elif slry_for_tax <= 1500:
        tax = slry_for_tax * 0.03
    elif slry_for_tax <= 4500:
        tax = slry_for_tax * 0.1 - 105
    elif slry_for_tax <= 9000:
        tax = slry_for_tax * 0.2 - 555
    elif slry_for_tax <= 35000:
        tax = slry_for_tax * 0.25 - 1005
    elif slry_for_tax <= 55000:
        tax = slry_for_tax * 0.3 - 2755
    elif slry_for_tax <= 80000:
        tax = slry_for_tax * 0.35 - 5505
    else:
        tax = slry_for_tax * 0.45 - 13505
    print(f'您的月薪是：{salary}')
    print(f'您需要缴纳的个人所得税是：{tax}')