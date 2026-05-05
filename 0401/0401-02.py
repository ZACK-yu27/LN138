# 创建一个元素都是数值的列表
numbers = [5, 10, 3]

# 用append()在末尾添加数字
numbers.append(8)
numbers.append(2)
numbers.append(3)

# 用extend()扩展列表
numbers.extend([8, 2])

# 用+扩展列表
numbers = numbers + [7, 1]

# 用insert()插入元素（在索引2的位置插入6）
numbers.insert(2, 6)

print("列表内容:", numbers)

# 用del删除索引3的元素
del numbers[3]
print("删除索引3后的列表:", numbers)

# 用pop()删除并返回最后一个元素
popped = numbers.pop()
print("用pop()删除的元素:", popped)
print("pop()后列表:", numbers)

# 用remove()删除值为6的元素
numbers.remove(6)
print("remove(6)后列表:", numbers)

# 对列表进行排序
numbers.sort()
print("排序后的列表:", numbers)

# 用参数reverse反转列表的排序
numbers.sort(reverse=True)
print("反转排序后的列表:", numbers)

# 求最大、最小值、和
max_num = max(numbers)
min_num = min(numbers)
sum_num = sum(numbers)
print("最大值:", max_num)
print("最小值:", min_num)
print("和:", sum_num)