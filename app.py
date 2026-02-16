import streamlit as st
import os
from dotenv import load_dotenv

# Page Config
st.set_page_config(page_title="Auto Writer AI", page_icon="✍️", layout="wide")

# Title
st.title("✍️ ハイパー記事作成くん")

# Sidebar: API Key
st.sidebar.header("セッティング")
load_dotenv()
default_api_key = os.getenv("GEMINI_API_KEY", "")

# Use Session State for API Key
if "api_key" not in st.session_state:
    st.session_state["api_key"] = default_api_key

api_key_input = st.sidebar.text_input("Gemini API Key", value=st.session_state["api_key"], type="password")
if api_key_input:
    st.session_state["api_key"] = api_key_input

st.markdown("""
### ようこそ
このツールは **Gemini 3.0 Pro (Preview)** を使用した記事自動生成ツールです。

#### 機能一覧
1.  **Generator (記事作成)**: 左のメニューから `1_Generator` を選択してください。
2.  **Prompt Editor (プロンプト管理)**: 記事タイプごとのプロンプトや出力先の設定ができます。
3.  **Site Config (パーツ管理)**: サイトごとの共通パーツや共通ルールを管理します。

#### クイックスタート
1.  左のサイドバーに API Key が入力されていることを確認してください。
2.  メニューから `1_Generator` を開きます。
3.  スプレッドシートのURLを入力して実行してください。
""")

if not st.session_state["api_key"]:
    st.warning("⚠️ 左のサイドバーでGemini API Keyを設定してください。")
else:
    st.success("✅ API Key設定済み")

