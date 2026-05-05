"""
可视化模块
股票数据可视化，包括K线图、均线、成交量和MACD
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.figure import Figure
from typing import Optional, Tuple
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
rcParams['axes.unicode_minus'] = False


class StockVisualizer:
    """股票数据可视化器"""

    def __init__(
        self,
        fig_size: Tuple[int, int] = (16, 10),
        dpi: int = 100
    ):
        """
        初始化可视化器
        :param fig_size: 图表尺寸
        :param dpi: 分辨率
        """
        self.fig_size = fig_size
        self.dpi = dpi
        self.fig: Optional[Figure] = None
        self.ma1_period = 5
        self.ma2_period = 10

    def _prepare_dates(self, df: pd.DataFrame) -> np.ndarray:
        """准备日期数据"""
        if 'date' in df.columns:
            dates = pd.to_datetime(df['date'])
            return mdates.date2num(dates)
        return np.arange(len(df))

    def _draw_candlestick(
        self,
        ax,
        dates: np.ndarray,
        ohlc: pd.DataFrame,
        width: float = 0.6
    ):
        """
        绘制K线图
        :param ax: 坐标轴
        :param dates: 日期数组
        :param ohlc: OHLC数据
        :param width: K线宽度
        """
        for i, (date, row) in enumerate(zip(dates, ohlc.iterrows())):
            row = row[1]
            open_price = row['open']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']

            if close_price >= open_price:
                color = 'red'
                body_bottom = open_price
                body_height = close_price - open_price
            else:
                color = 'green'
                body_bottom = close_price
                body_height = open_price - close_price

            if body_height < 0.01:
                body_height = 0.01
                ax.plot([date, date], [low_price, high_price], color=color, linewidth=0.5)
            else:
                ax.plot([date, date], [low_price, high_price], color=color, linewidth=0.5)

                rect = Rectangle(
                    (date - width / 2, body_bottom),
                    width,
                    body_height,
                    facecolor=color if close_price >= open_price else color,
                    edgecolor=color,
                    linewidth=0.5
                )
                ax.add_patch(rect)

    def _draw_ma_lines(
        self,
        ax,
        dates: np.ndarray,
        df: pd.DataFrame,
        ma1_period: int,
        ma2_period: int
    ):
        """
        绘制均线
        :param ax: 坐标轴
        :param dates: 日期数组
        :param df: 数据
        :param ma1_period: 短期均线周期
        :param ma2_period: 长期均线周期
        """
        ma1_color = '#FF6B6B'
        ma2_color = '#4ECDC4'

        ax.plot(
            dates,
            df['MA1'].values,
            color=ma1_color,
            linewidth=1.5,
            label=f'MA{ma1_period}'
        )

        ax.plot(
            dates,
            df['MA2'].values,
            color=ma2_color,
            linewidth=1.5,
            label=f'MA{ma2_period}'
        )

        ax.legend(loc='upper left', fontsize=9)

    def _draw_volume(self, ax, dates: np.ndarray, df: pd.DataFrame):
        """
        绘制成交量
        :param ax: 坐标轴
        :param dates: 日期数组
        :param df: 数据
        """
        colors = ['red' if df.iloc[i]['close'] >= df.iloc[i]['open'] else 'green'
                  for i in range(len(df))]

        ax.bar(dates, df['volume'].values / 10000, width=0.6, color=colors, alpha=0.7)

        ax.set_ylabel('Volume (10K)', fontsize=10)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))

    def _draw_macd(
        self,
        ax,
        dates: np.ndarray,
        df: pd.DataFrame
    ):
        """
        绘制MACD
        :param ax: 坐标轴
        :param dates: 日期数组
        :param df: 数据
        """
        dif = df['DIF'].values
        dea = df['DEA'].values
        macd = df['MACD'].values

        ax.plot(dates, dif, color='#FF6B6B', linewidth=1.2, label='DIF')
        ax.plot(dates, dea, color='#4ECDC4', linewidth=1.2, label='DEA')

        colors = ['red' if m >= 0 else 'green' for m in macd]
        ax.bar(dates, macd, width=0.6, color=colors, alpha=0.7, label='MACD')

        ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)
        ax.legend(loc='upper left', fontsize=9)
        ax.set_ylabel('MACD', fontsize=10)

    def create_chart(
        self,
        df: pd.DataFrame,
        stock_code: str,
        stock_name: Optional[str] = None,
        ma1_period: Optional[int] = None,
        ma2_period: Optional[int] = None
    ) -> Figure:
        """
        创建完整股票图表
        :param df: 股票数据
        :param stock_code: 股票代码
        :param stock_name: 股票名称
        :param ma1_period: 第一条均线周期
        :param ma2_period: 第二条均线周期
        :return: 图表对象
        """
        if ma1_period is not None:
            self.ma1_period = ma1_period
        if ma2_period is not None:
            self.ma2_period = ma2_period

        from data_processor import DataProcessor
        df = DataProcessor.process_stock_data(df, self.ma1_period, self.ma2_period)

        if self.fig is not None:
            plt.close(self.fig)

        self.fig = plt.figure(figsize=self.fig_size, dpi=self.dpi)

        gs = self.fig.add_gridspec(
            4, 1,
            height_ratios=[3, 0.8, 0.8, 0.8],
            hspace=0.1
        )

        ax_kline = self.fig.add_subplot(gs[0])
        ax_volume = self.fig.add_subplot(gs[1], sharex=ax_kline)
        ax_macd = self.fig.add_subplot(gs[2], sharex=ax_kline)
        ax_price = self.fig.add_subplot(gs[3], sharex=ax_kline)

        dates = self._prepare_dates(df)

        self._draw_candlestick(ax_kline, dates, df)
        self._draw_ma_lines(ax_kline, dates, df, self.ma1_period, self.ma2_period)

        ax_kline.set_ylabel('Price', fontsize=10)
        ax_kline.set_title(
            f'{stock_name or stock_code} ({stock_code}) K-Line Chart',
            fontsize=14,
            fontweight='bold'
        )
        ax_kline.grid(True, alpha=0.3)
        ax_kline.set_xlim(dates[0] - 1, dates[-1] + 1)

        self._draw_volume(ax_volume, dates, df)
        ax_volume.grid(True, alpha=0.3)

        self._draw_macd(ax_macd, dates, df)
        ax_macd.grid(True, alpha=0.3)

        ax_price.plot(dates, df['close'].values, color='#2196F3', linewidth=1)
        ax_price.set_ylabel('Price', fontsize=10)
        ax_price.set_xlabel('Date', fontsize=10)
        ax_price.grid(True, alpha=0.3)

        ax_kline.set_xticks([])
        ax_volume.set_xticks([])
        ax_macd.set_xticks([])

        date_labels = df['date'].iloc[::max(1, len(df)//10)]
        ax_price.set_xticks(mdates.date2num(pd.to_datetime(date_labels)))
        ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        plt.setp(ax_kline.get_xticklabels(), visible=False)
        plt.setp(ax_volume.get_xticklabels(), visible=False)
        plt.setp(ax_macd.get_xticklabels(), visible=False)

        self.fig.autofmt_xdate()

        return self.fig

    def update_ma_parameters(
        self,
        df: pd.DataFrame,
        stock_code: str,
        ma1_period: int,
        ma2_period: int,
        stock_name: Optional[str] = None
    ) -> Figure:
        """
        更新均线参数并重新绘图
        :param df: 股票数据
        :param stock_code: 股票代码
        :param ma1_period: 第一条均线周期
        :param ma2_period: 第二条均线周期
        :param stock_name: 股票名称
        :return: 新的图表对象
        """
        self.ma1_period = ma1_period
        self.ma2_period = ma2_period
        return self.create_chart(df, stock_code, stock_name, ma1_period, ma2_period)

    @staticmethod
    def show():
        """显示图表"""
        plt.show()

    @staticmethod
    def close():
        """关闭图表"""
        plt.close('all')


class InteractiveVisualizer(StockVisualizer):
    """交互式可视化器，支持缩放和平移"""

    def __init__(self, fig_size: Tuple[int, int] = (16, 10), dpi: int = 100):
        super().__init__(fig_size, dpi)

    def create_interactive_chart(
        self,
        df: pd.DataFrame,
        stock_code: str,
        stock_name: Optional[str] = None,
        ma1_period: Optional[int] = None,
        ma2_period: Optional[int] = None
    ) -> Figure:
        """
        创建交互式图表
        :param df: 股票数据
        :param stock_code: 股票代码
        :param stock_name: 股票名称
        :param ma1_period: 第一条均线周期
        :param ma2_period: 第二条均线周期
        :return: 图表对象
        """
        fig = self.create_chart(df, stock_code, stock_name, ma1_period, ma2_period)

        fig.canvas.mpl_connect('scroll_event', self._on_scroll)
        fig.canvas.mpl_connect('button_press_event', self._on_click)
        fig.canvas.mpl_connect('motion_notify_event', self._on_motion)

        self._pan_start = None
        self._ax_limits = None

        return fig

    def _on_scroll(self, event):
        """鼠标滚轮缩放"""
        if event.inaxes is None:
            return

        scale_factor = 1.1 if event.button == 'up' else 0.9

        ax = event.inaxes
        xlim = ax.get_xlim()
        x_range = xlim[1] - xlim[0]
        x_center = (xlim[0] + xlim[1]) / 2

        new_x_range = x_range * scale_factor
        new_xlim = (x_center - new_x_range / 2, x_center + new_x_range / 2)

        for axes in self.fig.axes:
            axes.set_xlim(new_xlim)

        self.fig.canvas.draw()

    def _on_click(self, event):
        """鼠标点击事件"""
        if event.button == 2:
            self._pan_start = (event.xdata, event.ydata)
            self._ax_limits = [(ax.get_xlim(), ax.get_ylim()) for ax in self.fig.axes]

    def _on_motion(self, event):
        """鼠标移动事件（平移）"""
        if self._pan_start is None or event.inaxes is None:
            return

        dx = event.xdata - self._pan_start[0]

        for ax, (xlim, ylim) in zip(self.fig.axes, self._ax_limits):
            ax.set_xlim((xlim[0] - dx, xlim[1] - dx))

        self.fig.canvas.draw()


if __name__ == "__main__":
    from data_fetcher import StockDataFetcher
    from data_processor import DataProcessor

    fetcher = StockDataFetcher()
    df, msg = fetcher.fetch_stock_data("000001")

    if df is not None:
        visualizer = StockVisualizer()
        fig = visualizer.create_chart(df, "000001", "Ping An Bank", 5, 10)
        plt.show()

    fetcher.logout()