title = '清华大学出版社（TSINGHUA UNIVERSITY PRESS）'

bgn_idx = title.find('清')
end_idx = title.find('社')

print(f'提取的字符串为：{title[bgn_idx:end_idx+1]}\n')