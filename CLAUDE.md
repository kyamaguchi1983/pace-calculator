# pace-calculator — 800m のレースペース計算（Streamlit）

ゴールタイムから、区間ごとの速度と通過タイムを出す。レースパターン（ALL・POS・MED・NEG）ごとに比べる。
dev 全体の決まり（開発の流れ・作業の終了・安全）はそのまま当てはまる。ここにはこのリポジトリだけのことを書く。

## 開発の流れ

- 段階 A（手元で main に取り込んで push する）。
- ただし main に push すると、公開中のアプリが作り直される見込み（下の「デプロイ」）。push の前に手元で画面を確かめる。

## 確認

- 確認: `uv run python -c "from pace_calc import parse_time, calc_splits, PATTERNS; print(calc_splits(800, 800/parse_time('2:01.35'), PATTERNS['MED']))"`（区間・速度・経過タイムの 3 つのリストが出れば OK）
- 画面で見るときは `uv sync` のあと `uv run streamlit run pace_app.py` を実行し、http://localhost:8501 を開く。
- テストはない。

## 構成

- `pace_calc.py`: 計算の本体。コマンドラインでも動く（`uv run python pace_calc.py 800 2:01.35`）。
- `pace_app.py`: Streamlit の画面。計算は `pace_calc.py` の関数を読み込んで使う。計算・相対速度・パターンの名前と色を変えると両方に効く。グラフの描き方だけは両方のファイルに別々に書いてある（`pace_calc.py` の `show_speed_graph` と `pace_app.py`）。
- 区間ごとの相対速度は `pace_calc.py` の固定値（文献の Table 5-7・5-8 から。文献名はコードにない）。
- `main.py` は `uv init` で作られた雛形のまま。使っていない。

## デプロイ

- Streamlit Community Cloud。公開 URL は README.md にある。
- GitHub の main と連携していて、push で自動で作り直される見込み。設定ファイル（`.streamlit/` など）はリポジトリにない。
- Streamlit Cloud の設定画面で要確認: メインファイル（たぶん `pace_app.py`）、Python の版、依存を `uv.lock` と `requirements.txt` のどちらから読んでいるか。
  - 2026-11-20 に依存を上げたあと、公開中のアプリは Streamlit 1.65.0 で動いた。3.11 以上の Python なら 1.67.0 が入るので、Python は 3.10 の見込み。`requires-python` を 3.11 以上に上げるのは、設定画面で Python の版を確かめて上げてから（先に上げると、公開中のアプリが依存を入れられずに止まるおそれがある）。
- 長く使われないと休止する（開くと「This app has gone to sleep」と出る。ボタンを押すと 30 秒ほどで起きる）。

## 記録先

- 作業ログは worklog.md（2026-11-20 から）。CHANGELOG はない。

## データの扱い

- 個人情報は扱わない。入力はゴールタイムとレースパターンの選択だけで、保存・送信・ログインはない。

## 注意

- 公開リポジトリ。個人名・メールアドレス・秘密情報を書かない。
- 依存は `pyproject.toml`・`uv.lock`（uv）と `requirements.txt`（版の固定なし）の二重。依存を足すときは `uv add` のあと、`requirements.txt` にも同じ名前を足す。
- `.gitignore` は `.env*` や `.streamlit/secrets.toml` を除外していない。秘密情報を使うときは、先に `.gitignore` に足す。
- `beep_timer.py` と `*.png` は `.gitignore` で除外した手元だけのファイル。GitHub にはない。
- コード内のコメントは `pip install ...` を案内しているが、今は uv で管理している。
