GZ = {'location':'华南', 'population': 15000000, 'area': 7434}
CS = {'location':'华中', 'population': 8000000, 'area': 11819}
SH = {'location':'华东', 'population': 24000000, 'area': 6340}

cities = {'广州': GZ, '长沙': CS, '上海': SH}

for city, info in cities.items():
    print(f"{city}位于{info['location']}，人口{info['population']}，面积{info['area']}平方公里")