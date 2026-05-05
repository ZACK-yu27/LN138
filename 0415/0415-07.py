day_one = {
    "招商银行": 1.24,
    "兴业银行": 1.11,
    "宁波银行": 0.36,
    "上海银行": 0.33,
    "浦发银行": 0.00,
    "工商银行": -0.71,
    "中国银行": -0.78,
    "农业银行": -0.80,
    "建设银行": -0.86
}

day_two = {
    "兴业银行": 2.31,
    "浦发银行": 1.02,
    "建设银行": 0.20,
    "农业银行": 0.20,
    "工商银行": 0.00,
    "中国银行": -0.65,
    "宁波银行": -1.02,
    "招商银行": -2.03,
    "上海银行": -2.13
}

from collections import Counter
day_one_pos = {bank: change for bank, change in day_one.items() if change > 0}
day_two_pos = {bank: change for bank, change in day_two.items() if change > 0}

day_one_neg = {bank: change for bank, change in day_one.items() if change < 0}
day_two_neg = {bank: change for bank, change in day_two.items() if change < 0}

day_one_stable = {bank: change for bank, change in day_one.items() if change == 0}
day_two_stable = {bank: change for bank, change in day_two.items() if change == 0}

ALA_one_day_pos = set(day_one_pos.keys()) | set(day_two_pos.keys())
day_one_neg_day_two_pos = set(day_one_neg.keys()) & set(day_two_pos.keys())
day_one_neg_day_two_not_neg = set(day_one_neg.keys()) ^ (set(day_two_pos.keys()) | set(day_two_stable.keys()))
only_one_day_pos = (set(day_one_pos.keys()) | set(day_two_pos.keys())) - (set(day_one_pos.keys()) ^ set(day_two_pos.keys()))

print("至少一天上涨的股票：", ALA_one_day_pos)
print("第一天下跌第二天上涨的股票：", day_one_neg_day_two_pos)
print("第一天下跌第二天不跌的股票：", day_one_neg_day_two_not_neg)
print("仅一天上涨的股票：", only_one_day_pos)
