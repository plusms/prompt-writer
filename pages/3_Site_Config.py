import streamlit as st
import os

st.set_page_config(page_title="Site Config", page_icon="⚙️", layout="wide")

st.title("⚙️ サイト・ルール設定 (Site Config)")

RULES_FILE = "config/common_rules.md"
PARTS_DIR = "config/parts"

tab1, tab2 = st.tabs(["共通ルール (Common Rules)", "サイト別パーツ (Site Parts)"])

# Tab 1: Common Rules
with tab1:
    st.subheader("全記事共通ルール")
    rules_content = ""
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            rules_content = f.read()
            
    new_rules = st.text_area("共通ルール編集", value=rules_content, height=500)
    
    if st.button("ルールを保存"):
        with open(RULES_FILE, 'w', encoding='utf-8') as f:
            f.write(new_rules)
        st.toast("共通ルールを保存しました", icon="✅")

# Tab 2: Site Parts
with tab2:
    st.subheader("サイト別パーツ設定 (.md)")
    
    # List files
    if not os.path.exists(PARTS_DIR):
        os.makedirs(PARTS_DIR)
        
    # Option to Upload File
    uploaded_file = st.file_uploader("ファイルをアップロード (既存ファイルを上書きします)", type=["md", "txt"])
    if uploaded_file:
        # Save uploaded file
        save_path = os.path.join(PARTS_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.toast(f"{uploaded_file.name} をアップロード・保存しました", icon="✅")
        st.rerun()

    files = [f for f in os.listdir(PARTS_DIR) if f.endswith(".md")]
    
    selected_file = st.selectbox("編集するファイルを選択", ["(新規作成)"] + files)
    
    file_name_input = ""
    file_content = ""
    
    if selected_file == "(新規作成)":
        file_name_input = st.text_input("新規ファイル名 (例: mysite.md)")
    else:
        file_name_input = st.text_input("ファイル名", value=selected_file, disabled=True)
        path = os.path.join(PARTS_DIR, selected_file)
        with open(path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
    new_content = st.text_area("パーツ内容 (Markdown/HTML)", value=file_content, height=400)
    
    if st.button("パーツを保存"):
        if not file_name_input:
            st.error("ファイル名を入力してください")
        else:
            save_path = os.path.join(PARTS_DIR, file_name_input)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            st.toast(f"{file_name_input} を保存しました", icon="✅")
            st.rerun()
