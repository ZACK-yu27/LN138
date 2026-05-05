'''
提交期中小测的注意事项:
#1: 此文件为期中小测模板, 请保留预设的变量名称.
#2: 下载此模板后,请另存为mt_学号.py文件
#3: 代码截止提交时间:2026-4-29 16:20,
#4: 提交网址: https://pan.sysu.edu.cn/link/AAFCF0C579798F48AEB3DBCC3293125E55，
# 密码为ZvAd
#5: 请提交.py文件, 注意字符编码为utf-8
'''
'''-----------------重要提示-------------------
* 所提交的.py文件, 必须确保可运行(无异常), 仔细核对上传的文件和原文件无差异
*----------------------------------------------'''

# 学号（请写你的学号）：24314008
# 姓名：曾可涵


''' Q1 列表处理'''
# Q1.1 构建一个城市列表cityList，其中元素是自己想去旅游的全球城市,
# 构建另一个名人列表personList，其中元素是你自己知道的名人姓名,
# (要求两个列表的元素各不少于 4 个, 名称可以虚构, 名称可以是中文或者英文)
# 请在下方写你的代码

cityList = ["东京", "巴黎", "纽约", "伦敦", "悉尼"]
personList = ["马斯克", "爱因斯坦", "居里夫人", "贝多芬", "牛顿"]

# Q1.2 复制问题Q1.1的其中一个列表，合并另外一个列表到新复制的列表
#（要求：不得改变Q1.1构建的两个列表cityList和personList）,
# 新复制的列表名称为combinedList, combinedList 的元素顺序为：cityList的元素排在personList的元素之前

combinedList = cityList.copy()
combinedList.extend(personList)

tempList_1 = combinedList.copy()  # 请不要改变此句

# Q1.3 首先, 将合并后的列表combinedList倒序输出，
# 然后，删除原combinedList（即未经排序的）其中的第 2、5 两个元素后再输出
# 因此，此问题应该有2个输出的结果

# 下面写倒序输出代码，倒序排列的列表存放在reversecombinedList
reversecombinedList = combinedList[::-1]
print("倒序输出:", reversecombinedList)

tempList_2 = combinedList.copy() # 请不要改变此语句
# 下面写删除列表combinedList的第 2、5 两个元素后(combinedList改变）,
# 再输出列表combinedList代码

del combinedList[4]
del combinedList[1]
print("删除第2、5个元素后:", combinedList)



# Q1.4 生成一个新列表comboList，元素是最初构建的两个列表(cityList和personList)中各取一个元素组成的所有可能组合，
# 组合后的元素, 其形式为 "张三在广州", 其中'张三'是人名,'广州'是城市名.
# 输出新生成的列表；

comboList = []
for person in personList:
    for city in cityList:
        comboList.append(f"{person}在{city}")
print("组合列表:", comboList)


'''----------------Q1 问题结束------------------------'''

''' Q2 字典处理'''

# Q2.1 构建一个字典university，里面存放全球大学的信息.
# 要求至少2所大学，每所大学至少有2项信息：所在城市和学生数量（城市名称和学生数量允许虚构）

university = {
    "哈佛大学": {"城市": "剑桥市", "学生数量": 20000},
    "斯坦福大学": {"城市": "帕洛阿尔托", "学生数量": 17000}
}


# Q2.2 向字典university添加某一大学的所有信息.

university["麻省理工学院"] = {"城市": "剑桥市", "学生数量": 11000}


# Q2.3 在某一现有的大学中，添加一个新信息(例如学校的占地面积，其值允许虚构).

university["哈佛大学"]["占地面积"] = "5000亩"


# Q2.4 逐一输出每所大学的学生数量；计算所有大学的平均学生数，并输出。

total_students = 0
for uni_name, uni_info in university.items():
    students = uni_info["学生数量"]
    print(f"{uni_name}的学生数量: {students}")
    total_students += students

average_students = total_students / len(university)
print(f"平均学生数: {average_students}")


'''----------------Q2 问题结束------------------------'''

''' Q3 程序控制'''
# 某批发商根据客户采购的商品数量确定批发价格，
# 采购 10 件以下，按正常价格125元/件；
# 采购 10 件（含）到 20 件，打 9 折；
# 采购 20 件（含）到 40 件，打 8 折；
# 采购 40 件（含）以上，打 6.5 折。
# 写一个程序，完成以下任务：

# Q3.1 不断循环，根据用户输入的商品采购数量，输出相应的单价和总销售额；
# 要求：
# (1）若用户输入'quit'，则退出程序；
# (2）如果用户输入的有误，进行异常处理，并提示错误

base_price = 125

while [1]:    # 在下面继续完成循环程序，此句上面也可以添加代码
	try:
		user_input = input("请输入采购数量（或输入'quit'退出）：")
		if user_input == 'quit':
			print("程序已退出")
			break

		quantity = int(user_input)

		if quantity < 0:
			print("错误：采购数量不能为负数")
			continue

		if quantity < 10:
			discount = 1.0
		elif quantity < 20:
			discount = 0.9
		elif quantity < 40:
			discount = 0.8
		else:
			discount = 0.65

		unit_price = base_price * discount
		total_sales = unit_price * quantity

		print(f"单价: {unit_price}元/件")
		print(f"总销售额: {total_sales}元")

	except ValueError:
		print("错误：输入无效，请输入整数或'quit'")



'''----------------Q3 问题结束------------------------'''

