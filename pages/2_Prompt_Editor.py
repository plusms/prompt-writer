import streamlit as st
import json
import os

st.set_page_config(page_title="Prompt Editor", page_icon="📝", layout="wide")

st.title("📝 プロンプト管理 (Prompt Editor)")

PROMPTS_FILE = "config/prompts.json"

# Load logic
def load_prompts():
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_prompts(data):
    with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    st.toast("保存しました！", icon="✅")

prompts_data = load_prompts()

# Sidebar: Select Type
types = list(prompts_data.keys())
selected_type = st.sidebar.selectbox("記事タイプ選択", types)

# Add New Type
new_type = st.sidebar.text_input("新規タイプ追加")
if st.sidebar.button("追加"):
    if new_type and new_type not in prompts_data:
        prompts_data[new_type] = prompts_data.get("Default", {}).copy() # Clone Default
        save_prompts(prompts_data)
        st.rerun()

st.header(f"設定: {selected_type}")

if selected_type:
    current_data = prompts_data[selected_type]
    
    # Steps Tabs
    steps = ["Initial", "STEP 1", "STEP 1.5", "STEP 2", "STEP 3", "STEP 4", "STEP 4.5", "STEP 5", "STEP 6", "STEP 7"]
    tabs = st.tabs(steps + ["Mappings (Beta)"])

    # Edit Steps
    for i, step in enumerate(steps):
        with tabs[i]:
            val = current_data.get(step, "")
            
            # Default values
            exec_val = ""
            check_val = ""
            
            if isinstance(val, dict):
                # New Structure
                exec_val = val.get("exec", "")
                check_val = val.get("check", "")
            else:
                # Legacy String Structure - Try to auto-split
                if "**【自己チェック】**" in val:
                    parts = val.split("**【自己チェック】**")
                    exec_val = parts[0].replace("**【実行内容】**", "").strip()
                    check_val = parts[1].strip()
                else:
                    exec_val = val
                    check_val = ""

            st.markdown(f"### {step} 設定")
            
            # Two columns for inputs
            c1, c2 = st.columns(2)
            with c1:
                new_exec = st.text_area("実行内容 (Execution)", value=exec_val, height=400, key=f"{selected_type}_{step}_exec")
            with c2:
                new_check = st.text_area("自己チェック (Self-Check)", value=check_val, height=400, key=f"{selected_type}_{step}_check")
            
            # Update data structure (in memory)
            # using dict structure now
            current_data[step] = {
                "exec": new_exec,
                "check": new_check
            }
    
    # Edit Mappings
    with tabs[-1]:
        st.markdown("### 出力先マッピング設定")
        st.info("各ステップの出力結果をスプレッドシートのどの列（番号）に保存するか設定します。")
        
        current_mappings = current_data.get("mappings", {})
        # Convert to JSON string for editing
        mappings_json = json.dumps(current_mappings, indent=4, ensure_ascii=False)
        
        new_mappings_json = st.text_area("Mappings (JSON)", value=mappings_json, height=400)
        
        if st.button("マッピングを更新"):
            try:
                parsed_mappings = json.loads(new_mappings_json)
                current_data["mappings"] = parsed_mappings
                st.toast("マッピングを更新しました (保存ボタンを押して確定してください)", icon="✅")
            except json.JSONDecodeError:
                st.error("JSON形式が不正です")

    if st.button("変更を保存"):
        prompts_data[selected_type] = current_data
        save_prompts(prompts_data)
