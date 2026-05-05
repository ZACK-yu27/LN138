import math

#纸的厚度为1mm
thick = 1e-3

#地月距离
distance = 3.8712e8

#求折叠多少次能超过地月距离
fold = math.ceil(math.log(distance / thick, 2))
print(f"折叠{fold}次能超过地月距离")