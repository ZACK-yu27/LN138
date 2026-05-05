import pandas as pd
import numpy as np

np.random.seed(42)

n_rows = 1000

data = {
    'ID': range(1, n_rows + 1),
    '姓名': [f'用户{i}' for i in range(1, n_rows + 1)],
    '年龄': np.random.randint(18, 80, n_rows),
    '性别': np.random.choice(['男', '女'], n_rows),
    '城市': np.random.choice(['北京', '上海', '广州', '深圳', '杭州'], n_rows),
    '收入': np.random.uniform(3000, 50000, n_rows).round(2),
    '满意度': np.random.randint(1, 11, n_rows),
    '注册日期': pd.date_range('2020-01-01', periods=n_rows, freq='H').strftime('%Y-%m-%d'),
    '是否会员': np.random.choice([True, False], n_rows),
    '购买次数': np.random.randint(0, 50, n_rows)
}

for i in range(50):
    idx = np.random.randint(0, n_rows)
    data['收入'][idx] = np.nan
    if i < 30:
        data['城市'][np.random.randint(0, n_rows)] = np.nan

df = pd.DataFrame(data)

df.to_csv('sample_data.csv', index=False, encoding='utf-8-sig')
df.to_excel('sample_data.xlsx', index=False, engine='openpyxl')

print(f"样本数据已创建: {n_rows} 行 x {len(df.columns)} 列")
print(f"列: {list(df.columns)}")
print(df.head())