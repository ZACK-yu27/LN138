scores_dict = {
    "1001": [85, 90, 78],
    "1002": [92, 88, 95],
    "1003": [76, 82, 80],
    "1004": [90, 92, 88, 95],
    "1005": [60, 75, 70],
}

print("学生成绩管理系统")
print("=" * 30)
print("学号列表：", list(scores_dict.keys()))
print("=" * 30)

while True:
    student_id = input("请输入学号（输入quit退出）：")

    if student_id == 'quit':
        print("程序结束")
        break

    try:
        scores = scores_dict[student_id]
        average = sum(scores) / len(scores)
        print(f"学号 {student_id} 的平均成绩：{average:.2f}")
    except KeyError:
        print("学号有误")
