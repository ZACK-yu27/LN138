#等额本息还款法

total = float(input("贷款总额："))
rate = float(input("年利率："))
term = int(input("贷款年限：")) * 12

#计算每月还款金额
amount = (total * rate/12 * pow(1 + rate/12, term))\
      / (pow(1 + rate/12, term) - 1)
print(f"每月还款金额为{amount:.2f}")