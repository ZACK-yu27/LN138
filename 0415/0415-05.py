GZ_price = {'香蕉': 3.5, '苹果': 5.0, '芒果': 4.0}
CS_price = {'香蕉': 3.0, '苹果': 4.5, '橙子': 4.5}
SH_price = {'香蕉': 3.8, '苹果': 5.5, '橙子': 4.2}
BJ_price = {'苹果': 4.8, '橙子': 4.1}

from collections import Counter
banana_price = {'广州': GZ_price.get('香蕉', 0), '长沙': CS_price.get('香蕉', 0), '上海': SH_price.get('香蕉', 0), '北京': BJ_price.get('香蕉', 0)}
bnn_values = Counter(banana_price.values())
none = bnn_values[0] if 0 in bnn_values else 0
bnn_P = sum(banana_price.values()) / (len(banana_price) - none)
print(f'香蕉的平均价格是{bnn_P:.2f}元')
print(none)