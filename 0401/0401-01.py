list = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]

print(f"第5个元素是: {list[5]}")
print(f"第4个到第12个元素是: {list[3:12]}")
print(f"第2、4、6、8、10个元素是: {list[0:10:2]}")
print(f"倒置后的列表是: {list[::-1]}")

print(f"列表的长度是: {len(list)}")

ls = list
ls[0] = 0
print(f"在列表第0个位置替换为0后的列表是: {ls}；长度为: {len(ls)}")

lt = list.copy()
lt[0] = 0
print(f"在列表第0个位置替换为0后的列表是: {lt}；长度为: {len(lt)}")

print(f"列表中元素5的个数是: {list.count(5)}")