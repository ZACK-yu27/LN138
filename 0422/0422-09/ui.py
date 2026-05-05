"""
用户交互模块
提供命令行界面和参数调整功能
"""

import sys
from typing import Optional, Tuple
from datetime import datetime


class StockUI:
    """股票程序用户界面"""

    WELCOME_MSG = """
╔═══════════════════════════════════════════════════════════╗
║            股票数据获取与可视化系统 v1.0                   ║
║                   欢迎使用本系统                           ║
╚═══════════════════════════════════════════════════════════╝
"""

    MENU = """
┌─────────────────────────────────────────────────────────────┐
│                        功能菜单                             │
├─────────────────────────────────────────────────────────────┤
│  1. 查询股票数据                                            │
│  2. 调整均线参数                                            │
│  3. 重新加载数据                                            │
│  4. 查看帮助                                                │
│  5. 退出系统                                                │
└─────────────────────────────────────────────────────────────┘
请输入选项 (1-5): """

    HELP_MSG = """
┌─────────────────────────────────────────────────────────────┐
│                           帮助                              │
├─────────────────────────────────────────────────────────────┤
│ 【股票代码输入】                                            │
│   - A股市场: 6位数字 (如: 600000, 000001)                  │
│   - 创业板:   以3开头 (如: 300001)                          │
│   - 科创板:   以688开头 (如: 688001)                       │
│                                                             │
│ 【均线参数说明】                                            │
│   - MA5:  5日移动平均线 (短期趋势)                          │
│   - MA10: 10日移动平均线 (中期趋势)                         │
│   - 常用组合: 5&10, 10&20, 20&60                           │
│                                                             │
│ 【交互操作】                                                │
│   - 鼠标滚轮: 缩放图表                                      │
│   - 中键拖动: 平移查看                                     │
│   - 退出图表后可继续操作                                   │
│                                                             │
│ 【MACD指标说明】                                            │
│   - DIF (快线): 12日EMA - 26日EMA                          │
│   - DEA (慢线): DIF的9日EMA                                │
│   - MACD柱: 2*(DIF-DEA)                                    │
└─────────────────────────────────────────────────────────────┘
"""

    @staticmethod
    def print_welcome():
        """打印欢迎信息"""
        print(StockUI.WELCOME_MSG)

    @staticmethod
    def print_menu():
        """打印菜单"""
        print(StockUI.MENU, end='')

    @staticmethod
    def print_help():
        """打印帮助信息"""
        print(StockUI.HELP_MSG)

    @staticmethod
    def get_stock_code() -> Optional[str]:
        """
        获取股票代码输入
        :return: 股票代码或None(取消)
        """
        print("\n" + "=" * 50)
        print("【股票查询】")
        print("=" * 50)

        while True:
            code = input("请输入股票代码 (6位数字, 输入Q返回): ").strip().upper()

            if code == 'Q':
                return None

            if not code:
                print("错误: 股票代码不能为空，请重新输入")
                continue

            if not code.isdigit():
                print("错误: 股票代码只能包含数字，请重新输入")
                continue

            if len(code) != 6:
                print("错误: 股票代码应为6位数字，请重新输入")
                continue

            return code

    @staticmethod
    def get_ma_parameters() -> Tuple[Optional[int], Optional[int]]:
        """
        获取均线参数
        :return: (MA1周期, MA2周期) 或 (None, None)取消
        """
        print("\n" + "=" * 50)
        print("【均线参数调整】")
        print("=" * 50)

        print("\n常用均线组合:")
        print("  1. 5日 & 10日 (短期)")
        print("  2. 10日 & 20日 (中期)")
        print("  3. 20日 & 60日 (长期)")
        print("  4. 自定义参数")

        while True:
            choice = input("\n请选择 (1-4, 输入Q返回): ").strip()

            if choice.upper() == 'Q':
                return None, None

            if choice == '1':
                return 5, 10
            elif choice == '2':
                return 10, 20
            elif choice == '3':
                return 20, 60
            elif choice == '4':
                return StockUI._get_custom_ma_parameters()
            else:
                print("错误: 无效选择，请重新输入")

    @staticmethod
    def _get_custom_ma_parameters() -> Tuple[int, int]:
        """获取自定义均线参数"""
        while True:
            try:
                ma1 = int(input("请输入第一条均线周期 (MA1): ").strip())

                if ma1 <= 0:
                    print("错误: 周期必须为正整数")
                    continue

                if ma1 > 250:
                    print("警告: 周期过大可能会影响显示效果")

                ma2 = int(input("请输入第二条均线周期 (MA2): ").strip())

                if ma2 <= 0:
                    print("错误: 周期必须为正整数")
                    continue

                if ma2 > 250:
                    print("警告: 周期过大可能会影响显示效果")

                if ma1 == ma2:
                    print("提示: 两条均线周期相同，可考虑使用不同周期")

                return ma1, ma2

            except ValueError:
                print("错误: 请输入有效的数字")

    @staticmethod
    def show_loading(message: str = "处理中"):
        """显示加载状态"""
        print(f"\n⏳ {message}...", end='', flush=True)

    @staticmethod
    def show_success(message: str = "完成"):
        """显示成功信息"""
        print(f"\n✅ {message}")

    @staticmethod
    def show_error(message: str = "发生错误"):
        """显示错误信息"""
        print(f"\n❌ 错误: {message}")

    @staticmethod
    def show_warning(message: str = "警告"):
        """显示警告信息"""
        print(f"\n⚠️  {message}")

    @staticmethod
    def show_info(message: str):
        """显示信息"""
        print(f"\nℹ️  {message}")

    @staticmethod
    def display_stock_summary(summary: dict):
        """
        显示股票摘要信息
        :param summary: 股票摘要字典
        """
        if not summary:
            return

        print("\n" + "=" * 50)
        print("【股票行情摘要】")
        print("=" * 50)
        print(f"日期:     {summary.get('date', 'N/A')}")
        print(f"开盘价:   {summary.get('open', 'N/A'):.2f}" if isinstance(summary.get('open'), (int, float)) else f"开盘价:   {summary.get('open', 'N/A')}")
        print(f"最高价:   {summary.get('high', 'N/A'):.2f}" if isinstance(summary.get('high'), (int, float)) else f"最高价:   {summary.get('high', 'N/A')}")
        print(f"最低价:   {summary.get('low', 'N/A'):.2f}" if isinstance(summary.get('low'), (int, float)) else f"最低价:   {summary.get('low', 'N/A')}")
        print(f"收盘价:   {summary.get('close', 'N/A'):.2f}" if isinstance(summary.get('close'), (int, float)) else f"收盘价:   {summary.get('close', 'N/A')}")

        change = summary.get('change', 0)
        change_pct = summary.get('change_pct', 0)
        if isinstance(change, (int, float)) and isinstance(change_pct, (int, float)):
            sign = '+' if change > 0 else ''
            print(f"涨跌额:   {sign}{change:.2f}")
            print(f"涨跌幅:   {sign}{change_pct:.2f}%")

        print(f"成交量:   {summary.get('volume', 'N/A'):,}" if isinstance(summary.get('volume'), (int, float)) else f"成交量:   {summary.get('volume', 'N/A')}")

        print("-" * 50)
        print("【技术指标】")

        if summary.get('ma5'):
            print(f"MA5:      {summary.get('ma5'):.2f}")
        if summary.get('ma10'):
            print(f"MA10:     {summary.get('ma10'):.2f}")

        if summary.get('dif') is not None:
            print(f"DIF:      {summary.get('dif'):.2f}")
        if summary.get('dea') is not None:
            print(f"DEA:      {summary.get('dea'):.2f}")
        if summary.get('macd') is not None:
            macd_val = summary.get('macd')
            print(f"MACD:     {'+' if macd_val > 0 else ''}{macd_val:.2f}")

        print("=" * 50)

    @staticmethod
    def confirm(message: str) -> bool:
        """
        确认提示
        :param message: 提示信息
        :return: 用户选择
        """
        while True:
            choice = input(f"{message} (Y/N): ").strip().upper()
            if choice == 'Y':
                return True
            elif choice == 'N':
                return False
            else:
                print("请输入 Y 或 N")

    @staticmethod
    def pause():
        """暂停等待用户操作"""
        input("\n按回车键继续...")

    @staticmethod
    def clear_screen():
        """清屏"""
        import os
        os.system('cls' if sys.platform == 'win32' else 'clear')


class ProgressBar:
    """进度条显示"""

    def __init__(self, total: int = 100, width: int = 50):
        """
        初始化进度条
        :param total: 总数
        :param width: 进度条宽度
        """
        self.total = total
        self.width = width
        self.current = 0

    def update(self, current: int = None):
        """
        更新进度
        :param current: 当前进度
        """
        if current is not None:
            self.current = current
        else:
            self.current += 1

        percent = self.current / self.total
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)

        print(f'\r进度: [{bar}] {percent*100:.1f}%', end='', flush=True)

        if self.current >= self.total:
            print()

    def reset(self):
        """重置进度条"""
        self.current = 0


if __name__ == "__main__":
    StockUI.print_welcome()
    StockUI.print_help()

    code = StockUI.get_stock_code()
    print(f"\n输入的股票代码: {code}")

    ma1, ma2 = StockUI.get_ma_parameters()
    print(f"\n均线参数: MA{ma1}, MA{ma2}")