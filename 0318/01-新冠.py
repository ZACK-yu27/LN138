import math

#感染人数100人
speed = 100

#每人每天感染人数3.77人，求3天后感染人数
count = math.ceil(pow(1 + 3.77, 3) * speed )
print(f"3天后感染人数为{count}人")

#感染4亿人所需天数
day = math.ceil(math.log(400000000 / speed, 1 + 3.77))
print(f"感染4亿人需要{day}天")