months_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month = int(input("请输入月份（阿拉伯数字）："))
month_order = month - 1
print(f"第{month}个月是{months_short[month_order]}")