#!/usr/bin/env python3
# ============================================================
# pace_app.py - 800m レースペース計算 Streamlit ウェブアプリ
# ============================================================
# 起動方法:
#   streamlit run pace_app.py
#
# 必要ライブラリ:
#   pip install streamlit plotly
# ============================================================
import streamlit as st
import plotly.graph_objects as go

from pace_calc import (
    parse_time,
    calc_splits,
    PATTERNS,
    PATTERN_LABELS,
    PATTERN_COLORS,
)

# --- ページ設定 ---
st.set_page_config(
    page_title="800m Pace Calculator",
    page_icon="🏃",
    layout="wide",
)

# --- サイドバー: 入力フォーム ---
st.sidebar.title("800m Pace Calculator")

distance = 800.0

time_str = st.sidebar.text_input(
    "Time (mm:ss or seconds)",
    value="2:01.35",
    placeholder="2:01.35",
)

pattern_choice = st.sidebar.radio(
    "Race Pattern",
    options=["ALL", "POS", "MED", "NEG"],
    format_func=lambda k: f"{k} - {PATTERN_LABELS[k]}",
    index=0,
)

# --- メイン: 計算 & 表示 ---
try:
    total_sec = parse_time(time_str)
except (ValueError, IndexError):
    st.error("Time format error. Use mm:ss (e.g. 2:01.35) or seconds (e.g. 121.35)")
    st.stop()

if total_sec <= 0:
    st.error("Time must be greater than 0.")
    st.stop()

mps = distance / total_sec
kmh = mps * 3.6
pace_per_km = 1000 / mps
pace_mm = int(pace_per_km // 60)
pace_ss = pace_per_km % 60

# --- Pace Report (メトリクス) ---
st.header("Pace Report")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Distance", f"{distance:.0f} m")
col2.metric("Time", f"{time_str}  ({total_sec:.2f}s)")
col3.metric("Avg Speed", f"{mps:.2f} m/s  |  {kmh:.2f} km/h")
col4.metric("1km Pace", f"{pace_mm}:{pace_ss:05.2f} /km")

# --- パターン計算 ---
pattern_keys = list(PATTERNS.keys()) if pattern_choice == "ALL" else [pattern_choice]

all_results = {}
for key in pattern_keys:
    labels, speeds, times = calc_splits(distance, mps, PATTERNS[key])
    all_results[key] = (labels, speeds, times)

# --- Plotly グラフ ---
st.header("Speed Chart")

fig = go.Figure()
for key, (labels, speeds, _times) in all_results.items():
    fig.add_trace(go.Scatter(
        x=labels,
        y=speeds,
        mode="lines+markers",
        name=f"{key} ({PATTERN_LABELS[key]})",
        line=dict(color=PATTERN_COLORS[key], width=2),
        marker=dict(size=8),
        hovertemplate="%{x}<br>%{y:.2f} m/s<extra></extra>",
    ))

fig.add_hline(
    y=mps,
    line_dash="dash",
    line_color="gray",
    annotation_text=f"Average: {mps:.2f} m/s",
    annotation_position="right",
)

if len(pattern_keys) == 1:
    title = f"800m Race Pattern - {pattern_keys[0]} ({PATTERN_LABELS[pattern_keys[0]]})"
else:
    title = "800m Race Patterns - Speed Comparison"

fig.update_layout(
    title=dict(text=title, font=dict(size=16)),
    xaxis_title="Section",
    yaxis_title="Speed (m/s)",
    xaxis=dict(type="category"),
    hovermode="x unified",
    template="plotly_white",
    showlegend=True,
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

# --- スプリットテーブル ---
st.header("Split Table")

for key in pattern_keys:
    labels, speeds, times = all_results[key]
    st.subheader(f"{key} - {PATTERN_LABELS[key]}")

    rows = []
    for label, spd, t in zip(labels, speeds, times):
        mm = int(t // 60)
        ss = t % 60
        rows.append({
            "Section": label,
            "Elapsed": f"{mm}:{ss:05.2f}",
            "Speed (m/s)": f"{spd:.2f}",
            "Speed (km/h)": f"{spd * 3.6:.2f}",
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)
