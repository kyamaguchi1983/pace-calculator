# pace-calculator

800m のレースペースを計算するツール。ゴールタイムから、区間ごとの速度と通過タイムを出す。

レースパターンは ALL（全体平均）・POS（前半型）・MED（イーブン）・NEG（後半型）の 4 つ。ALL を選ぶと 4 つを並べて比べる。

## 公開中のアプリ

Streamlit でアプリを公開中。

https://pace-calculator-a9mseg4p6rijhtdejta99q.streamlit.app/

## 手元で動かす

uv を使う。

```sh
uv sync
uv run streamlit run pace_app.py
```

ブラウザで http://localhost:8501 を開く。

コマンドラインでも計算できる。

```sh
uv run python pace_calc.py 800 2:01.35                  # 4 つのパターンを比べる
uv run python pace_calc.py 800 2:01.35 --pattern MED    # パターンを 1 つ選ぶ
```
