from collections import Counter

# 原始数据（每行：工号、姓名、部门、邮箱）
data = [
    [10932, '张珊', '管理', 'zhans@163.com'],
    [10933, '李思', '软件', 'lisi@qq.com'],
    [10934, '王武', '财务', 'wangwu@hotmail.com'],
    [10935, '赵柳', '财务', 'zhaoliu@163.com'],
    [10936, '钱棋', '人事', 'qianqi@qq.com'],
    [10941, '张明', '管理', 'zhangming@qq.com'],
    [10942, '赵敏', '人事', 'zhaomin@163.com'],
    [10945, '王红', '培训', 'wanghong@hotmail.com'],
    [10946, '李萧', '培训', 'lixiao@hotmail.com'],
    [10947, '孙科', '软件', 'sunke@163.com'],
    [10948, '刘利', '软件', 'liuli@qq.com']
]

# 提取部门列表和邮箱服务器列表
departments = [row[2] for row in data]          # 部门在索引2
email_servers = [row[3].split('@')[1] for row in data]  # 取@后面的部分

# 统计
dept_counter = Counter(departments)
email_counter = Counter(email_servers)

# 输出结果
print("各部门人数：")
for dept, count in dept_counter.items():
    print(f"{dept}: {count}人")

print("各邮箱服务器使用人数：")
for server, count in email_counter.items():
    print(f"{server}: {count}人")