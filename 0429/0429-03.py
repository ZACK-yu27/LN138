scores = []

while True:
    score_input = input("请输入成绩：")

    try:
        s = float(score_input)
        if s < 0 or s > 100:
            print("成绩必须在0-100之间")
            continue
        valid = True
        score = s
    except ValueError:
        print("输入无效，请输入数字")
        continue

    scores.append(score)

    while True:
        continue_input = input("是否继续输入成绩（y/n）：")
        if continue_input in ['y', 'Y', 'n', 'N']:
            break
        print("输入有误，请重新输入")

    if continue_input in ['n', 'N']:
        break

if scores:
    average = sum(scores) / len(scores)
    print(f"共输入 {len(scores)} 个成绩")
    print(f"平均成绩：{average}")
else:
    print("没有输入任何成绩")
