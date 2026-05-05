x = [7, 3, 7, 2, 8, 8, 1]
x_sorted = sorted(x)
max = x_sorted[len(x_sorted) - 1]

for i in range(len(x)):
	if x[i] == max:
		print(i)
		break

print(x)
print(x_sorted)