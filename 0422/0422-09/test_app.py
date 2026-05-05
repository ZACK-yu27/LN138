from data_fetcher import StockDataFetcher
from data_processor import DataProcessor
import matplotlib
matplotlib.use('Agg')
from visualizer import StockVisualizer

print("开始测试完整流程...")

fetcher = StockDataFetcher()
df, msg = fetcher.fetch_stock_data('000001')

if df is not None:
    print(f"数据获取成功，共{len(df)}条记录")

    processed = DataProcessor.process_stock_data(df, 5, 10)
    summary = DataProcessor.get_stock_summary(processed)
    print(f"\n股票摘要: {summary}")

    print("\n开始生成图表...")
    visualizer = StockVisualizer()
    fig = visualizer.create_chart(df, "000001", "平安银行", 5, 10)
    print("图表生成成功")

    import os
    output_path = os.path.join(os.path.dirname(__file__), 'stock_chart.png')
    fig.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"图表已保存到: {output_path}")

else:
    print(f"数据获取失败: {msg}")

fetcher.logout()
print("测试完成")