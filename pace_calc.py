#!/usr/bin/env python3
# ============================================================
# pace_calc.py - 800m レースペース計算ツール
# ============================================================
# 使い方:
#   python pace_calc.py <距離(m)> <タイム>
#
# 例:
#   python pace_calc.py 800 2:01.35              # 全パターン比較 (デフォルト)
#   python pace_calc.py 800 2:01.35 --pattern POS  # ポジティブスプリット
#   python pace_calc.py 800 2:01.35 --pattern MED  # イーブンペース
#   python pace_calc.py 800 2:01.35 --pattern NEG  # ネガティブスプリット
#
# オプション:
#   --pattern {POS,MED,NEG,ALL}  レースパターン選択 (既定: ALL)
#     POS : ポジティブスプリット (前半型)
#     MED : イーブンペース (均等型)
#     NEG : ネガティブスプリット (後半型)
#     ALL : 全パターン一括比較
#
# 必要ライブラリ:
#   pip install plotly argparse
#
# ウェブ版 (Streamlit):
#   pip install streamlit plotly
#   streamlit run pace_app.py
# ============================================================
import argparse

def parse_time(ts: str) -> float:
    # "2:01.35" など mm:ss(.ms) を秒に
    if ":" in ts:
        m, s = ts.split(":")
        return int(m) * 60 + float(s)
    return float(ts)

# 区間定義
SECTIONS = [
    (0, 120), (120, 200), (200, 300), (300, 400),
    (400, 500), (500, 600), (600, 700), (700, 800),
]

# 800mレースの典型的なペースパターン (Table 5-7: 全体平均)
RACE_PATTERN_ALL = {
    (0, 120): 103.37, (120, 200): 104.99, (200, 300): 100.34, (300, 400): 98.48,
    (400, 500): 98.48,  (500, 600): 99.53,  (600, 700): 98.75,  (700, 800): 97.45,
}

# Table 5-8: POS (ポジティブスプリット) - 前半速く後半減速
RACE_PATTERN_POS = {
    (0, 120): 104.34, (120, 200): 105.83, (200, 300): 101.71, (300, 400): 99.39,
    (400, 500): 99.12,  (500, 600): 98.94,  (600, 700): 97.44,  (700, 800): 95.07,
}

# Table 5-8: MED (イーブンペース) - 比較的均等
RACE_PATTERN_MED = {
    (0, 120): 102.68, (120, 200): 104.89, (200, 300): 100.34, (300, 400): 98.47,
    (400, 500): 97.29,  (500, 600): 98.75,  (600, 700): 99.65,  (700, 800): 99.39,
}

# Table 5-8: NEG (ネガティブスプリット) - 後半加速
RACE_PATTERN_NEG = {
    (0, 120): 102.06, (120, 200): 103.48, (200, 300): 97.80, (300, 400): 96.81,
    (400, 500): 98.16,  (500, 600): 101.20, (600, 700): 100.53, (700, 800): 100.46,
}

PATTERNS = {
    "ALL": RACE_PATTERN_ALL,
    "POS": RACE_PATTERN_POS,
    "MED": RACE_PATTERN_MED,
    "NEG": RACE_PATTERN_NEG,
}

PATTERN_LABELS = {
    "ALL": "Average (Table 5-7)",
    "POS": "Positive Split",
    "MED": "Medium / Even",
    "NEG": "Negative Split",
}

PATTERN_COLORS = {
    "ALL": "black",
    "POS": "red",
    "MED": "blue",
    "NEG": "green",
}

def get_relative_speed(distance_m: float, pattern: dict) -> float:
    """指定距離地点での相対速度を取得 (%)"""
    for (start, end), speed in pattern.items():
        if start <= distance_m < end:
            return speed
    return list(pattern.values())[-1]

def calculate_split_time(start_m: float, end_m: float, avg_mps: float, pattern: dict) -> float:
    """区間タイムを計算（1m刻みで積分）"""
    total_time = 0.0
    for d in range(int(start_m), int(end_m)):
        rel_speed = get_relative_speed(d, pattern) / 100.0
        actual_mps = avg_mps * rel_speed
        total_time += 1.0 / actual_mps
    return total_time

def calc_splits(distance, mps, pattern):
    """指定パターンでスプリットを計算し、ラベルと速度のリストを返す"""
    split_points = [end for (start, end) in SECTIONS if end <= distance + 1e-9]
    acc = 0.0
    prev_d = 0
    labels = []
    speeds = []
    times = []

    for d in split_points:
        seg_len = d - prev_d
        split_time = calculate_split_time(prev_d, d, mps, pattern)
        acc += split_time
        segment_mps = seg_len / split_time
        labels.append(f"{int(prev_d)}~{int(d)}m")
        speeds.append(segment_mps)
        times.append(acc)
        prev_d = d

    return labels, speeds, times

def print_splits(labels, speeds, times, pattern_name):
    """スプリット表をコンソールに出力"""
    print(f"\n[Splits - {pattern_name} ({PATTERN_LABELS[pattern_name]})]")
    for label, spd, t in zip(labels, speeds, times):
        kmh = spd * 3.6
        mm = int(t // 60); ss = t % 60
        print(f"  {label:>12s}  {mm}:{ss:05.2f}  {spd:.2f} m/s  {kmh:.2f} km/h")

def main():
    p = argparse.ArgumentParser(description="Track pace calculator")
    p.add_argument("distance", type=float, help="走距離 (m) 例: 800")
    p.add_argument("time", help="ゴールタイム (mm:ss または 秒) 例: 2:01.35")
    p.add_argument("--pattern", default="ALL", choices=["POS", "MED", "NEG", "ALL"],
                   help="レースパターン: POS(前半型) MED(イーブン) NEG(後半型) ALL(全体平均) 既定:ALL")
    args = p.parse_args()

    total_sec = parse_time(args.time)
    mps = args.distance / total_sec
    kmh = mps * 3.6
    pace_per_km = 1000 / mps

    print(f"\n=== Pace Report ===")
    print(f"距離: {args.distance:.0f} m")
    print(f"記録: {args.time}  ({total_sec:.2f} 秒)")
    print(f"平均速度: {mps:.2f} m/s  |  {kmh:.2f} km/h")
    mm = int(pace_per_km // 60); ss = pace_per_km % 60
    print(f"1kmペース: {mm}:{ss:05.2f} /km")

    # 選択されたパターンのスプリットを出力
    selected = args.pattern
    pattern_keys = list(PATTERNS.keys()) if selected == "ALL" else [selected]

    all_results = {}
    for key in pattern_keys:
        labels, speeds, times = calc_splits(args.distance, mps, PATTERNS[key])
        print_splits(labels, speeds, times, key)
        all_results[key] = (labels, speeds)

    # グラフ表示
    show_speed_graph(mps, all_results)

def show_speed_graph(mps, all_results):
    try:
        import plotly.graph_objects as go
        HAS_PLOTLY = True
    except ImportError:
        HAS_PLOTLY = False

    if not HAS_PLOTLY:
        print("plotlyが利用できません。インストール: pip install plotly")
        return

    fig = go.Figure()

    for key, (labels, speeds) in all_results.items():
        fig.add_trace(go.Scatter(
            x=labels,
            y=speeds,
            mode='lines+markers',
            name=f'{key} ({PATTERN_LABELS[key]})',
            line=dict(color=PATTERN_COLORS[key], width=2),
            marker=dict(size=8),
            hovertemplate='%{x}<br>%{y:.2f} m/s<extra></extra>'
        ))

    # 平均速度の水平線
    fig.add_hline(
        y=mps,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Average: {mps:.2f} m/s",
        annotation_position="right"
    )

    keys = list(all_results.keys())
    if len(keys) == 1:
        title = f"800m Race Pattern - {keys[0]} ({PATTERN_LABELS[keys[0]]})"
    else:
        title = "800m Race Patterns - Speed Comparison"

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='black')),
        xaxis_title="Section",
        yaxis_title="Speed (m/s)",
        xaxis=dict(type='category'),
        hovermode='x unified',
        template='plotly_white',
        showlegend=True
    )

    fig.show()

if __name__ == "__main__":
    main()
