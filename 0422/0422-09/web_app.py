"""
股票数据可视化 Web应用
Flask + Plotly 实现交互式股票图表
"""

from flask import Flask, render_template, request, jsonify
import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bs.login()


class StockDataHandler:
    """股票数据处理器"""

    @staticmethod
    def validate_stock_code(stock_code: str) -> Tuple[bool, str]:
        """验证股票代码"""
        if not stock_code:
            return False, "股票代码不能为空"
        stock_code = stock_code.strip().upper()
        if not stock_code.isdigit() or len(stock_code) != 6:
            return False, "股票代码应为6位数字"
        return True, ""

    @staticmethod
    def get_stock_code_prefix(stock_code: str) -> str:
        """获取股票代码前缀"""
        return "sh." if stock_code.startswith('6') else "sz."

    @staticmethod
    def fetch_stock_data(
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[Optional[pd.DataFrame], str]:
        """获取股票数据"""
        valid, error_msg = StockDataHandler.validate_stock_code(stock_code)
        if not valid:
            return None, error_msg

        if start_date is None:
            start_date = (datetime.now() - timedelta(days=1095)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        full_code = StockDataHandler.get_stock_code_prefix(stock_code) + stock_code

        rs = bs.query_history_k_data_plus(
            full_code,
            "date,code,open,high,low,close,volume,amount,pctChg",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"
        )

        if rs.error_code != '0':
            return None, f"数据获取失败: {rs.error_msg}"

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return None, "未获取到数据，请检查股票代码"

        df = pd.DataFrame(data_list, columns=rs.fields)
        df = df[df['volume'].astype(str).str.replace('.', '', 1).str.isdigit()]
        df = df[df['volume'].astype(float) > 0]

        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        return df, ""

    @staticmethod
    def calculate_ma(df: pd.DataFrame, period: int) -> pd.Series:
        """计算移动平均线"""
        return df['close'].rolling(window=period).mean()

    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算MACD"""
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        dif = exp1 - exp2
        dea = dif.ewm(span=signal, adjust=False).mean()
        macd_hist = 2 * (dif - dea)
        return dif, dea, macd_hist

    @staticmethod
    def process_data(
        df: pd.DataFrame,
        ma1_period: int = 5,
        ma2_period: int = 10
    ) -> Dict[str, Any]:
        """处理数据并生成图表数据"""
        df = df.copy()
        df['MA1'] = StockDataHandler.calculate_ma(df, ma1_period)
        df['MA2'] = StockDataHandler.calculate_ma(df, ma2_period)
        dif, dea, macd = StockDataHandler.calculate_macd(df)
        df['DIF'] = dif
        df['DEA'] = dea
        df['MACD'] = macd

        chart_data = {
            'dates': df['date'].dt.strftime('%Y-%m-%d').tolist(),
            'opens': df['open'].fillna(0).tolist(),
            'highs': df['high'].fillna(0).tolist(),
            'lows': df['low'].fillna(0).tolist(),
            'closes': df['close'].fillna(0).tolist(),
            'volumes': df['volume'].fillna(0).astype(int).tolist(),
            'pctChg': df['pctChg'].fillna(0).tolist(),
            'ma1': df['MA1'].fillna(0).tolist(),
            'ma2': df['MA2'].fillna(0).tolist(),
            'dif': df['DIF'].fillna(0).tolist(),
            'dea': df['DEA'].fillna(0).tolist(),
            'macd': df['MACD'].fillna(0).tolist(),
        }

        latest = df.iloc[-1] if len(df) > 0 else None
        summary = {}
        if latest is not None:
            prev = df.iloc[-2] if len(df) > 1 else latest
            change = latest['close'] - prev['close']
            change_pct = (change / prev['close'] * 100) if prev['close'] != 0 else 0
            summary = {
                'date': latest['date'].strftime('%Y-%m-%d'),
                'open': round(latest['open'], 2),
                'high': round(latest['high'], 2),
                'low': round(latest['low'], 2),
                'close': round(latest['close'], 2),
                'volume': int(latest['volume']),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'ma5': round(latest['MA1'], 2) if pd.notna(latest['MA1']) else None,
                'ma10': round(latest['MA2'], 2) if pd.notna(latest['MA2']) else None,
            }

        return {
            'chart_data': chart_data,
            'summary': summary,
            'record_count': len(df)
        }


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/stock', methods=['GET'])
def get_stock_data():
    """获取股票数据API"""
    stock_code = request.args.get('code', '').strip()
    ma1 = int(request.args.get('ma1', 5))
    ma2 = int(request.args.get('ma2', 10))

    if not stock_code:
        return jsonify({'success': False, 'error': '请输入股票代码'})

    df, error_msg = StockDataHandler.fetch_stock_data(stock_code)

    if df is None:
        return jsonify({'success': False, 'error': error_msg})

    result = StockDataHandler.process_data(df, ma1, ma2)
    result['success'] = True
    result['stock_code'] = stock_code

    return jsonify(result)


@app.route('/api/stock/summary', methods=['GET'])
def get_stock_summary():
    """获取股票简要信息"""
    stock_code = request.args.get('code', '').strip()

    if not stock_code:
        return jsonify({'success': False, 'error': '请输入股票代码'})

    df, error_msg = StockDataHandler.fetch_stock_data(stock_code)

    if df is None:
        return jsonify({'success': False, 'error': error_msg})

    result = StockDataHandler.process_data(df, 5, 10)
    result['success'] = True

    return jsonify(result)


@app.route('/api/stock/update-ma', methods=['GET'])
def update_ma_parameters():
    """更新均线参数API"""
    stock_code = request.args.get('code', '').strip()
    ma1 = int(request.args.get('ma1', 5))
    ma2 = int(request.args.get('ma2', 10))

    if not stock_code:
        return jsonify({'success': False, 'error': '请输入股票代码'})

    df, error_msg = StockDataHandler.fetch_stock_data(stock_code)

    if df is None:
        return jsonify({'success': False, 'error': error_msg})

    result = StockDataHandler.process_data(df, ma1, ma2)
    result['success'] = True

    return jsonify(result)


if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        bs.logout()