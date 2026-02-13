import streamlit as st
import json
import os
from main import process_batch

st.set_page_config(page_title="Generator - Auto Writer", page_icon="🚀", layout="wide")

st.title("🚀 記事作成 (Generator)")

# 1. Load Local Configs
PROMPTS_FILE = "config/prompts.json"
RULES_FILE = "config/common_rules.md"

def load_local_config():
    prompts = {}
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            prompts = json.load(f)
            
    rules = ""
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            rules = f.read()
    return prompts, rules

manual_prompts, manual_rules = load_local_config()

# 2. UI Inputs
if "api_key" not in st.session_state or not st.session_state["api_key"]:
    st.warning("⚠️ API Keyが設定されていません。Homeに戻って設定してください。")
    st.stop()

col1, col2 = st.columns([2, 1])

with col1:
    sheet_url = st.text_input("Google Sheet URL", placeholder="https://docs.google.com/spreadsheets/d/...")
    dry_run = st.checkbox("ドライラン (API消費なし)", value=False)
    
    st.info(f"現在の設定: プロンプト設定数={len(manual_prompts)}種, 共通ルール文字数={len(manual_rules)}文字")
    
    # Custom Logger
    class StreamlitLogger:
        def __init__(self, log_container, status_placeholder):
            self.log_container = log_container
            self.status_placeholder = status_placeholder
            self.logs = []
            
        def log(self, message):
            self.logs.append(message)
            self.log_container.code("\n".join(self.logs), language="text")
            if "Status Update:" in message:
                status_text = message.replace("Status Update:", "").strip()
                self.status_placeholder.info(status_text)

    if st.button("実行開始", type="primary"):
        if not sheet_url:
            st.error("URLを入力してください")
        else:
            log_container = st.empty()
            with col2:
                st.subheader("ステータス")
                status_ph = st.empty()
                status_ph.info("開始...")
            
            logger = StreamlitLogger(log_container, status_ph)
            
            try:
                # Call Main Process with Manual Configs
                process_batch(
                    api_key=st.session_state["api_key"],
                    sheet_url=sheet_url,
                    dry_run=dry_run,
                    log_callback=logger.log,
                    manual_prompts=manual_prompts,       # Inject Local Prompts
                    manual_common_rules=manual_rules    # Inject Local Rules
                )
                st.balloons()
                st.success("完了しました")
                status_ph.success("完了")
            except Exception as e:
                st.error(f"エラー: {e}")
                status_ph.error("停止")

with col2:
    if "status_ph" not in locals():
        st.subheader("ステータス")
        st.write("待機中...")
