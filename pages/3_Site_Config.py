import streamlit as st
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Site Config", page_icon="⚙️", layout="wide")

st.title("⚙️ サイト・ルール設定 (Site Config)")

# Load Secrets / Env
load_dotenv()
token = st.secrets.get("GITHUB_TOKEN") or st.secrets.get("github_token") or os.getenv("GITHUB_TOKEN")
repo = st.secrets.get("GITHUB_REPOSITORY") or st.secrets.get("github_repository") or os.getenv("GITHUB_REPOSITORY")

RULES_FILE = "config/common_rules.md"
PARTS_DIR = "config/parts"

# Helper for GitHub
def commit_file_to_github(file_path, content, message):
    if not token or not repo:
        st.error("GitHub連携が無効です。Secretsを設定してください。")
        return
    try:
        from github_handler import GitHubHandler
        gh = GitHubHandler(token, repo)
        success, msg = gh.commit_file(file_path, content, message)
        if success:
            st.toast(f"GitHubへ保存しました: {file_path}", icon="🚀")
            st.success(f"GitHubへコミットしました: {file_path}")
        else:
            st.error(f"GitHub保存エラー: {msg}")
    except Exception as e:
        st.error(f"予期せぬエラー: {e}")

tab1, tab2, tab3 = st.tabs(["共通ルール (Common Rules)", "サイト別パーツ (Site Parts)", "サイト接続設定 (sites.json)"])

# Tab 1: Common Rules
with tab1:
    st.subheader("全記事共通ルール")
    rules_content = ""
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            rules_content = f.read()
            
    new_rules = st.text_area("共通ルール編集", value=rules_content, height=500)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("ルールを保存 (一時保存)"):
            with open(RULES_FILE, 'w', encoding='utf-8') as f:
                f.write(new_rules)
            st.toast("共通ルールを一時保存しました", icon="✅")
            
    with col2:
        if token and repo:
            if st.button("GitHubにコミット (共通ルール)"):
                commit_file_to_github(RULES_FILE, new_rules, "Update common_rules.md")

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
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("パーツを保存 (一時保存)"):
            if not file_name_input:
                st.error("ファイル名を入力してください")
            else:
                save_path = os.path.join(PARTS_DIR, file_name_input)
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                st.toast(f"{file_name_input} を保存しました", icon="✅")
                st.rerun()
    
    with col2:
        if token and repo and selected_file != "(新規作成)":
             if st.button(f"GitHubにコミット ({selected_file})"):
                 # file_name_input is disabled but contains the name
                 target_file = f"config/parts/{selected_file}"
                 commit_file_to_github(target_file, new_content, f"Update parts: {selected_file}")
        elif token and repo and selected_file == "(新規作成)":
             if st.button("GitHubに新規作成"):
                 if not file_name_input:
                     st.error("ファイル名を入力してください")
                 else:
                     target_file = f"config/parts/{file_name_input}"
                     commit_file_to_github(target_file, new_content, f"Create parts: {file_name_input}")


# Tab 3: Sites Config
with tab3:
    st.subheader("WordPress接続設定 (sites.json)")
    SITES_FILE = "config/sites.json"
    
    current_sites = "{}"
    if os.path.exists(SITES_FILE):
        with open(SITES_FILE, 'r', encoding='utf-8') as f:
             current_sites = f.read()
    
    new_sites = st.text_area("JSON設定", value=current_sites, height=300)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("設定を保存 (一時保存)"):
            try:
                # Validate JSON
                import json
                json.loads(new_sites)
                with open(SITES_FILE, 'w', encoding='utf-8') as f:
                    f.write(new_sites)
                st.toast("保存しました", icon="✅")
            except json.JSONDecodeError:
                st.error("JSON形式が不正です。")
                
    with col2:
        if token and repo:
            if st.button("GitHubにコミット (sites.json)"):
                 try:
                    import json
                    json.loads(new_sites) # Validate before commit
                    commit_file_to_github(SITES_FILE, new_sites, "Update sites.json")
                 except json.JSONDecodeError:
                    st.error("JSON形式が不正です。コミットできません。")
