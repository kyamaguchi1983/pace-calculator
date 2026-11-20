# 作業ログ

## 2026-11-20 依存を上げた（Mac mini）

- **何を**: `uv lock --upgrade` で `uv.lock` の依存を上げた（ffd6aa9）。streamlit 1.54.0 → 1.65.0（Python 3.10）/ 1.67.0（3.11 以上）、plotly 6.5.2 → 7.1.0、pandas 2.3.3 → 2.3.3 / 3.1.1、pillow 12.1.1 → 12.3.0 / 13.0.0 など。GitPython と tornado は streamlit が使わなくなり、lock から消えた。あわせて、streamlit が廃止を知らせる `use_container_width=True` を `width="stretch"` に替えた（`pace_app.py` の 2 か所。見た目は同じ）。
- **なぜ**: GitHub の Dependabot の知らせが 122 件あった（critical 7。Pillow・GitPython・tornado・urllib3 ほか。どれも `uv.lock` の古い版が元）。
- **確かめたこと**: CLAUDE.md の確認の 1 行。画面を動かすテスト（streamlit の `AppTest` で、最初の表示・パターンの切り替え・タイムの入力・形式の誤り。Python 3.10 と 3.13 の両方で成功。テストのファイルはリポジトリに入れていない）。手元の画面（グラフと表）。push の後、公開中のアプリ（長く使われず休止していたので起こした）が開き、右上のメニューの表示が Streamlit v1.65.0 になった。
- **分かったこと**: 公開中のアプリは Streamlit 1.65.0 で動いている。3.11 以上の Python なら 1.67.0 が入るので、Streamlit Cloud の Python は 3.10 の見込み。
- **残り**: Pillow の知らせのうち、直った版が 13.0.0 のものは残る見込み（Python 3.10 では Pillow は 12.3.0 までしか入らない）。このアプリは画像を受け取らないので、影響は小さい見込み。消すには、Streamlit Cloud の Python を 3.11 以上にしてアプリを作り直し（設定画面。運用者）、そのあと `pyproject.toml` の `requires-python` と `.python-version` を上げて lock を作り直す。先に `requires-python` だけを上げると、公開中のアプリが依存を入れられずに止まるおそれがある。
