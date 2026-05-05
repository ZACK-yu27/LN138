#用range函数创建一个列表并输出
numbers = list(range(1, 6))
print(numbers[0])
print(numbers[1])
print(numbers[2])
print(numbers[3])
print(numbers[4])

#求每个元素的立方组成的列表
cubes = numbers.copy()
cubes[0] = numbers[0] ** 3
cubes[1] = numbers[1] ** 3
cubes[2] = numbers[2] ** 3
cubes[3] = numbers[3] ** 3
cubes[4] = numbers[4] ** 3
print(cubes)

#求立方和
sum_of_cubes = cubes[0] + cubes[1] + cubes[2] + cubes[3] + cubes[4]
print(f"立方和是: {sum_of_cubes}")