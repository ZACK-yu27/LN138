stoke_name = ('浦发银行','招商银行','保利地产','平安银行')
stoke_code = ('600000','600036','600048','000001')

while True:
    search_code = input('请输入要查找的股票代码：')
    if len(search_code) == 0:
        break
    if search_code not in stoke_code:
        print('该股票不在股票库中')
        continue
    print(f'{search_code}是{stoke_name[stoke_code.index(search_code)]}的股票代码')
    break