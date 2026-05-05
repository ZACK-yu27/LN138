money_str = input("输入带货币符号的金额：")
currency = money_str[0]
money = eval(money_str[1:])
if currency == '$':
    print(f'{money_str}等于人民币{money*7.2795}元')
else:
    print(f'{money_str}等于美元{money/7.2795}元')
