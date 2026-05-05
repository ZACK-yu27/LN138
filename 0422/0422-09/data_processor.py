"""
数据处理模块
处理股票数据，计算技术指标
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


class DataProcessor:
    """数据处理器"""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        计算移动平均线
        :param df: 股票数据
        :param period: 周期
        :param column: 计算列
        :return: MA序列
        """
        return df[column].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        计算指数移动平均线
        :param df: 股票数据
        :param period: 周期
        :param column: 计算列
        :return: EMA序列
        """
        return df[column].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算MACD指标
        :param df: 股票数据
        :param fast_period: 快线周期
        :param slow_period: 慢线周期
        :param signal_period: 信号线周期
        :return: (DIF, DEA, MACD柱状图)
        """
        exp1 = df['close'].ewm(span=fast_period, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow_period, adjust=False).mean()

        dif = exp1 - exp2
        dea = dif.ewm(span=signal_period, adjust=False).mean()
        macd_hist = 2 * (dif - dea)

        return dif, dea, macd_hist

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
        """
        计算RSI相对强弱指标
        :param df: 股票数据
        :param period: 周期
        :param column: 计算列
        :return: RSI序列
        """
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0,
        column: str = 'close'
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算布林带
        :param df: 股票数据
        :param period: 周期
        :param std_dev: 标准差倍数
        :param column: 计算列
        :return: (上轨, 中轨, 下轨)
        """
        middle = df[column].rolling(window=period).mean()
        std = df[column].rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    @staticmethod
    def process_stock_data(
        df: pd.DataFrame,
        ma1_period: int = 5,
        ma2_period: int = 10
    ) -> pd.DataFrame:
        """
        完整处理股票数据
        :param df: 原始股票数据
        :param ma1_period: 第一条均线周期
        :param ma2_period: 第二条均线周期
        :return: 处理后的数据
        """
        result = df.copy()

        result['MA1'] = DataProcessor.calculate_ma(result, ma1_period)
        result['MA2'] = DataProcessor.calculate_ma(result, ma2_period)

        dif, dea, macd_hist = DataProcessor.calculate_macd(result)
        result['DIF'] = dif
        result['DEA'] = dea
        result['MACD'] = macd_hist

        return result

    @staticmethod
    def get_stock_summary(df: pd.DataFrame) -> dict:
        """
        获取股票数据摘要
        :param df: 股票数据
        :return: 摘要信息字典
        """
        if df is None or df.empty:
            return {}

        latest = df.iloc[-1]
        previous = df.iloc[-2] if len(df) > 1 else latest

        change = latest['close'] - previous['close']
        change_pct = (change / previous['close']) * 100 if previous['close'] != 0 else 0

        return {
            'date': latest['date'].strftime('%Y-%m-%d') if hasattr(latest['date'], 'strftime') else str(latest['date']),
            'open': round(latest['open'], 2),
            'high': round(latest['high'], 2),
            'low': round(latest['low'], 2),
            'close': round(latest['close'], 2),
            'volume': int(latest['volume']),
            'amount': round(latest['amount'], 2) if pd.notna(latest['amount']) else 0,
            'change': round(change, 2),
            'change_pct': round(change_pct, 2),
            'ma5': round(latest['MA1'], 2) if pd.notna(latest.get('MA1')) else None,
            'ma10': round(latest['MA2'], 2) if pd.notna(latest.get('MA2')) else None,
            'dif': round(latest['DIF'], 2) if pd.notna(latest.get('DIF')) else None,
            'dea': round(latest['DEA'], 2) if pd.notna(latest.get('DEA')) else None,
            'macd': round(latest['MACD'], 2) if pd.notna(latest.get('MACD')) else None,
        }

    @staticmethod
    def filter_by_date_range(
        df: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        按日期范围筛选数据
        :param df: 股票数据
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 筛选后的数据
        """
        result = df.copy()

        if start_date:
            start = pd.to_datetime(start_date)
            result = result[result['date'] >= start]

        if end_date:
            end = pd.to_datetime(end_date)
            result = result[result['date'] <= end]

        return result.reset_index(drop=True)


if __name__ == "__main__":
    from data_fetcher import StockDataFetcher

    fetcher = StockDataFetcher()
    df, msg = fetcher.fetch_stock_data("000001")

    if df is not None:
        processed = DataProcessor.process_stock_data(df, 5, 10)
        summary = DataProcessor.get_stock_summary(processed)
        print("股票摘要:", summary)
        print("\n处理后数据:")
        print(processed.tail())

    fetcher.logout()