courses = {'CN': '语文', 'EN': '英语', 'MA': '数学'}
students = {('001', '小明'): [courses['CN'], courses['EN']], ('002', '小红'): [courses['MA'], courses['EN']], ('003', '小刚'): [courses['EN']]}

for name, course_list in students.items():
    print(f"{name[1]}（学号：{name[0]}）选修了{', '.join(course_list)}")