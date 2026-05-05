class_mate = {'小明': 18, '小红': 17, '小刚': 19}
friends = {'李华': 20, '王强': 21, '赵丽': 19}

#添加一个熟人
class_mate['小华'] = 18

#合并两个字典
shouren = {**class_mate, **friends}

#删除一个熟人
del class_mate['小刚']

#打印
print(shouren.items())
for name, age in shouren.items():
    print(f'{name}是{age}岁')