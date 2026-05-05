"""
股票数据获取与可视化系统
主程序入口
"""

import sys
import os

from data_fetcher import StockDataFetcher
from data_processor import DataProcessor
from visualizer import StockVisualizer
from ui import StockUI


class StockVisualizationApp:
    """股票可视化应用程序"""

    def __init__(self):
        self.fetcher = StockDataFetcher()
        self.visualizer = StockVisualizer()
        self.current_data = None
        self.current_code = None
        self.current_name = None
        self.ma1_period = 5
        self.ma2_period = 10

    def run(self):
        """运行应用程序"""
        StockUI.print_welcome()

        while True:
            try:
                StockUI.print_menu()
                choice = input().strip()

                if choice == '1':
                    self.query_stock()
                elif choice == '2':
                    self.adjust_ma_parameters()
                elif choice == '3':
                    self.reload_data()
                elif choice == '4':
                    StockUI.print_help()
                    StockUI.pause()
                elif choice == '5':
                    self.exit_app()
                    break
                else:
                    StockUI.show_error("无效选项，请重新选择")
            except KeyboardInterrupt:
                StockUI.show_info("\n\n检测到Ctrl+C，正在退出...")
                self.exit_app()
                break
            except Exception as e:
                StockUI.show_error(f"程序异常: {str(e)}")
                StockUI.pause()

    def query_stock(self):
        """查询股票数据"""
        code = StockUI.get_stock_code()
        if code is None:
            return

        StockUI.show_loading("正在获取股票数据")

        try:
            df, error_msg = self.fetcher.fetch_stock_data(code)

            if df is None:
                StockUI.show_error(error_msg)
                return

            self.current_data = df
            self.current_code = code

            StockUI.show_success(f"成功获取 {code} 的 {len(df)} 条历史数据")

            processed_df = DataProcessor.process_stock_data(df, self.ma1_period, self.ma2_period)
            summary = DataProcessor.get_stock_summary(processed_df)

            StockUI.display_stock_summary(summary)

            StockUI.show_info("正在生成图表...")

            self.visualizer = StockVisualizer()
            fig = self.visualizer.create_chart(
                df,
                code,
                stock_name=None,
                ma1_period=self.ma1_period,
                ma2_period=self.ma2_period
            )

            StockVisualizer.show()

        except ConnectionError:
            StockUI.show_error("网络连接失败，请检查网络设置")
        except Exception as e:
            StockUI.show_error(f"数据获取失败: {str(e)}")

    def adjust_ma_parameters(self):
        """调整均线参数"""
        if self.current_data is None:
            StockUI.show_warning("请先查询股票数据")
            return

        ma1, ma2 = StockUI.get_ma_parameters()

        if ma1 is None:
            return

        self.ma1_period = ma1
        self.ma2_period = ma2

        StockUI.show_success(f"均线参数已更新: MA{ma1}, MA{ma2}")

        if self.current_data is not None:
            StockUI.show_info("正在更新图表...")

            try:
                fig = self.visualizer.update_ma_parameters(
                    self.current_data,
                    self.current_code,
                    ma1,
                    ma2,
                    self.current_name
                )

                processed_df = DataProcessor.process_stock_data(self.current_data, ma1, ma2)
                summary = DataProcessor.get_stock_summary(processed_df)
                StockUI.display_stock_summary(summary)

                StockVisualizer.show()

            except Exception as e:
                StockUI.show_error(f"图表更新失败: {str(e)}")

    def reload_data(self):
        """重新加载数据"""
        if self.current_code is None:
            StockUI.show_warning("没有可重新加载的数据，请先查询股票")
            return

        if not StockUI.confirm(f"重新加载股票 {self.current_code} 的数据"):
            return

        StockUI.show_loading("正在重新加载数据")

        try:
            df, error_msg = self.fetcher.fetch_stock_data(self.current_code)

            if df is None:
                StockUI.show_error(error_msg)
                return

            self.current_data = df

            StockUI.show_success(f"数据已更新，共 {len(df)} 条记录")

            processed_df = DataProcessor.process_stock_data(df, self.ma1_period, self.ma2_period)
            summary = DataProcessor.get_stock_summary(processed_df)

            StockUI.display_stock_summary(summary)

            StockUI.show_info("正在生成图表...")

            fig = self.visualizer.create_chart(
                df,
                self.current_code,
                stock_name=self.current_name,
                ma1_period=self.ma1_period,
                ma2_period=self.ma2_period
            )

            StockVisualizer.show()

        except Exception as e:
            StockUI.show_error(f"数据重新加载失败: {str(e)}")

    def exit_app(self):
        """退出应用程序"""
        try:
            self.fetcher.logout()
        except:
            pass

        StockVisualizer.close()

        print("\n" + "=" * 50)
        print("感谢使用股票数据获取与可视化系统！")
        print("=" * 50)
        print("\n再见！👋\n")


def main():
    """主函数"""
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    app = StockVisualizationApp()
    app.run()


if __name__ == "__main__":
    main()