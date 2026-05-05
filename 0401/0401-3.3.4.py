#复利的基本信息
compond_rate = 0.03
years = 5

#用户输入目标中值
final_amt = float(input("请输入目标金额: "))

#计算初始投资金额
initial_amt = final_amt / (1 + compond_rate) ** years

#计算每年的本息余额
balance_list = []
balance = initial_amt
balance_1 = balance * (1 + compond_rate)
balance_2 = balance_1 * (1 + compond_rate)
balance_3 = balance_2 * (1 + compond_rate)
balance_list.extend([balance, balance_1, balance_2, balance_3])

#输出结果
print("初始投资金额: {:.2f}".format(balance_list[0]))
print("第一年末的本息余额: {:.2f}".format(balance_list[1]))
print("第二年末的本息余额: {:.2f}".format(balance_list[2]))
print("第三年末的本息余额: {:.2f}".format(balance_list[3]))
