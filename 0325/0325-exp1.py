content = '''         Sun Yat-sen University, founded by Dr. Sun Yat-sen, has an educational tradition spanning over 100 years. Under the direct supervision of the Ministry of Education of the People's Republic of China, and strongly supported by both the Ministry and Guangdong Province, Sun Yat-sen University has developed into a modern comprehensive university that enjoys a reputation as a top-tier university nationally and a renowned university internationally. With five campuses in the three cities of Guangzhou, Zhuhai and Shenzhen, and ten affiliated hospitals, the University is striving to become a world-class university and global center of learning.          '''

#使用标题字符串输出
print(f'使用标题字符串输出为：\n{content.title()}\n')

#使用大写字符串输出
print(f'使用大写字符串输出为：\n{content.upper()}\n')

#使用小写字符串输出
print(f'使用小写字符串输出为：\n{content.lower()}\n')

#使用strip()函数去掉字符串两端的空格
print(f'使用strip()函数去掉字符串两端的空格后为：\n{content.strip()}\n')

#使用lstrip()函数去掉字符串左端的空格
print(f'使用lstrip()函数去掉字符串左端的空格后为：\n{content.lstrip()}\n')

#使用rstrip()函数去掉字符串右端的空格
print(f'使用rstrip()函数去掉字符串右端的空格后为：\n{content.rstrip()}\n')

#计算字符串长度
print(f'字符串长度为：{len(content)}\n')

#使用count()函数计算字符串中单词"Sun Yat-sen University"出现的次数
print(f'单词"Sun Yat-sen University"在字符串中出现的次数为：{content.count("Sun Yat-sen University")}\n')

#在字符串中提取"Sun Yat-sen University"
print(f'提取的字符串为：{content[9:31]}\n')

#判断该字符串的开头单词是否为"Sun Yat-sen University"
print(f'该字符串的开头单词是否为"Sun Yat-sen University"：{content.startswith("Sun Yat-sen University")}\n')

#用split()函数分割字符串
print(f'分割后的字符串为：\n{content.split()}')