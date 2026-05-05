"""
股票数据获取模块
使用baostock接口获取股票历史交易数据
"""

import baostock as bs
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Tuple
import time


class StockDataFetcher:
    """股票数据获取器"""

    def __init__(self):
        """初始化baostock连接"""
        self._logged_in = False

    def login(self) -> bool:
        """登录baostock系统"""
        if not self._logged_in:
            lg = bs.login()
            if lg.error_code != '0':
                return False
            self._logged_in = True
        return True

    def logout(self):
        """登出baostock系统"""
        if self._logged_in:
            bs.logout()
            self._logged_in = False

    def validate_stock_code(self, stock_code: str) -> Tuple[bool, str]:
        """
        验证股票代码格式
        :param stock_code: 股票代码
        :return: (是否有效, 错误信息)
        """
        if not stock_code:
            return False, "股票代码不能为空"

        stock_code = stock_code.strip().upper()

        if len(stock_code) != 6:
            return False, "股票代码应为6位数字"

        if not stock_code.isdigit():
            return False, "股票代码只能包含数字"

        return True, ""

    def get_stock_code_prefix(self, stock_code: str) -> str:
        """
        获取股票代码前缀
        :param stock_code: 股票代码
        :return: 前缀(sz./sh.)
        """
        if stock_code.startswith('6'):
            return "sh."
        else:
            return "sz."

    def fetch_stock_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: str = "d"
    ) -> Tuple[Optional[pd.DataFrame], str]:
        """
        获取股票历史数据
        :param stock_code: 股票代码
        :param start_date: 开始日期 (YYYY-MM-DD)
        :param end_date: 结束日期 (YYYY-MM-DD)
        :param frequency: 数据频率 (d=日线, w=周线, m=月线)
        :return: (数据DataFrame, 错误信息)
        """
        valid, error_msg = self.validate_stock_code(stock_code)
        if not valid:
            return None, error_msg

        if not self.login():
            return None, "连接金融数据服务失败，请检查网络连接"

        if start_date is None:
            start_date = (datetime.now() - timedelta(days=1095)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        full_code = self.get_stock_code_prefix(stock_code) + stock_code

        rs = bs.query_history_k_data_plus(
            full_code,
            "date,code,open,high,low,close,volume,amount,turn,pctChg",
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag="2"
        )

        if rs.error_code != '0':
            return None, f"数据获取失败: {rs.error_msg}"

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return None, "未获取到数据，请检查股票代码是否正确"

        df = pd.DataFrame(data_list, columns=rs.fields)

        df = df[df['volume'] != '']
        df = df[df['volume'].astype(float) > 0]

        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'amount', 'turn', 'pctChg']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        return df, ""

    def fetch_realtime_quote(self, stock_code: str) -> Tuple[Optional[dict], str]:
        """
        获取实时行情数据
        :param stock_code: 股票代码
        :return: (行情数据字典, 错误信息)
        """
        valid, error_msg = self.validate_stock_code(stock_code)
        if not valid:
            return None, error_msg

        if not self.login():
            return None, "连接金融数据服务失败"

        full_code = self.get_stock_code_prefix(stock_code) + stock_code

        rs = bs.query_realtime_quotes(full_code)

        if rs.error_code != '0':
            return None, f"行情获取失败: {rs.error_msg}"

        if rs.next():
            data = rs.get_row_data()
            return {
                'code': data[0],
                'name': data[1],
                'open': data[2],
                'high': data[3],
                'low': data[4],
                'close': data[5],
                'volume': data[6],
                'amount': data[7]
            }, ""

        return None, "未获取到实时行情"


if __name__ == "__main__":
    fetcher = StockDataFetcher()
    df, msg = fetcher.fetch_stock_data("000001")
    if df is not None:
        print(df.head())
    else:
        print(f"Error: {msg}")
    fetcher.logout()