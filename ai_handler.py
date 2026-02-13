import os
import google.generativeai as genai
from typing import List, Dict
import time

class AIHandler:
    def __init__(self, api_key: str, vertex_project_id: str = None, vertex_location: str = "global", instruction_path: str = None, instruction_text: str = None):
        genai.configure(api_key=api_key)
        
        # User requested specific model "gemini-3-pro-preview"
        # We try this first. If it fails (invalid), we might need a fallback, 
        # but for now we trust the user's request.
        self.model_name = "gemini-3-pro-preview" 

        if instruction_text:
            self.system_instruction = instruction_text
        elif instruction_path:
            with open(instruction_path, 'r', encoding='utf-8') as f:
                self.system_instruction = f.read()
        else:
            raise ValueError("Either instruction_path or instruction_text must be provided.")

        print(f"Initializing Gemini with model: {self.model_name}")
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_instruction,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )

    def generate_article_flow(self, main_kw: str, sub_kws: str, goal: str, slug: str, prompt_dict: Dict[str, str], progress_callback=None, step_callback=None) -> Dict[str, str]:
        """
        Executes the multi-step flow using Gemini only.
        """
        chat = self.model.start_chat(history=[])
        full_log = "" 
        
        # 1. Prepare Initial Prompt
        initial_prompt_template = prompt_dict.get("Initial", "")
        if not initial_prompt_template:
            raise ValueError("No 'Initial' prompt found.")

        try:
            user_prompt = initial_prompt_template.format(
                main_kw=main_kw, sub_kws=sub_kws, goal=goal, slug=slug
            )
        except KeyError as e:
            print(f"Warning: Prompt format error {e}. Using raw prompt.")
            user_prompt = initial_prompt_template
        
        print(f"--- [Gemini] STEP 1: Initializing for '{main_kw}' ---")
        if progress_callback:
            progress_callback("STEP 1: Planning (Gemini)")
            
        try:
            response = self._send_message_with_retry(chat, user_prompt)
            full_log += f"\n\n--- User ---\n{user_prompt}\n\n--- Gemini ---\n{response.text}"
        except Exception as e:
            print(f"Initial prompt failed: {e}")
            return {"content": "", "image_prompts": "", "title": "", "description": ""}

        # 2. Loop through Steps
        step_keys = [k for k in prompt_dict.keys() if k.startswith("STEP")]
        
        for step in step_keys:
            prompt_data = prompt_dict[step]
            
            # Helper to build prompt string from Dict or String
            exec_text = ""
            check_text = ""
            
            if isinstance(prompt_data, dict):
                exec_text = prompt_data.get("exec", "")
                check_text = prompt_data.get("check", "")
            else:
                # Legacy String Structure - Try to auto-split
                val = prompt_data
                if "**【自己チェック】**" in val:
                    parts = val.split("**【自己チェック】**")
                    exec_text = parts[0].replace("**【実行内容】**", "").strip()
                    check_text = parts[1].strip()
                else:
                    exec_text = val
                    check_text = ""

            # Format prompt (slug/kw injection)
            try:
                # DEBUG LOGGING for Attribute Error investigation (Exec Text)
                if isinstance(exec_text, dict):
                    print(f"CRITICAL ERROR DETECTED at {step}: exec_text is a DICT!")
                    print(f"Content: {exec_text}")
                    exec_text = str(exec_text)

                # DEBUG LOGGING for Attribute Error investigation (Check Text)
                if isinstance(check_text, dict):
                    print(f"CRITICAL ERROR DETECTED at {step}: check_text is a DICT!")
                    print(f"Content: {check_text}")
                    check_text = str(check_text)

                formatted_exec = exec_text.format(slug=slug, main_kw=main_kw)
                formatted_check = check_text.format(slug=slug, main_kw=main_kw) if check_text else ""
            except Exception as e:
                print(f"Format Error at {step}: {e}")
                formatted_exec = exec_text
                formatted_check = check_text

            print(f"--- [Gemini] Proceeding to {step} ---")
            
            # PHASE 1: Execution (Draft)
            if progress_callback:
                progress_callback(f"{step} 実行中 (Draft)...")
                
            draft_prompt = f"""
            次の {step} を実行してください。

            {formatted_exec}
            
            出力をお願いします。
            """
            
            try:
                # 1. Draft
                response = self._send_message_with_retry(chat, draft_prompt)
                full_log += f"\n\n--- User ({step} - Draft) ---\n{draft_prompt}\n\n--- Gemini ---\n{response.text}"
                final_response_text = response.text
                
                # Callback for Draft (Optional mapping: "STEP X (Draft)")
                if step_callback:
                     step_callback(f"{step} (Draft)", response.text)

                # PHASE 2: Self-Check (Refine) - ONLY if check_text exists
                if formatted_check.strip():
                    if progress_callback:
                        progress_callback(f"{step} 自己チェック中 (Refine)...")
                    
                    refine_prompt = f"""
                    ありがとうございます。
                    直前の出力結果に対して、以下の【自己チェック基準】を用いて厳密にチェックし、
                    問題がある場合は修正した【最終結果】を出力してください。
                    問題がない場合も、そのまま出力してください。
                    
                    **【自己チェック基準】**
                    {formatted_check}
                    
                    出力は修正後のコンテンツのみをお願いします。
                    """
                    
                    response = self._send_message_with_retry(chat, refine_prompt)
                    full_log += f"\n\n--- User ({step} - Refine) ---\n{refine_prompt}\n\n--- Gemini ---\n{response.text}"
                    final_response_text = response.text

                # Callback with FINAL result
                if step_callback:
                    step_callback(step, final_response_text)

            except Exception as e:
                print(f"Error at {step}: {e}")
                import traceback
                traceback.print_exc()
                break
        
        return self._parse_output(full_log)
    
    def _send_message_with_retry(self, chat, content, retries=10, delay=30):
        from google.api_core import exceptions
        for attempt in range(retries):
            try:
                return chat.send_message(content)
            except exceptions.ResourceExhausted:
                print(f"[Gemini] Rate limit. Wait {delay}s... (Attempt {attempt+1}/{retries})")
                time.sleep(delay)
            except Exception as e:
                # If invalid model name, it might throw 404 or 400 here.
                if "404" in str(e) or "not found" in str(e).lower():
                    print(f"Error: Model {self.model_name} not found. Please check the model name.")
                raise e
        raise Exception("Gemini Max Retries")

    def _parse_output(self, text: str) -> Dict[str, str]:
        """
        Parses the full conversation log.
        """
        import re
        
        # 1. Image Prompts
        image_prompts = ""
        if "---IMAGE_START---" in text and "---IMAGE_END---" in text:
            pattern = re.compile(r"---IMAGE_START---(.*?)---IMAGE_END---", re.DOTALL)
            match = pattern.search(text)
            if match:
                image_prompts = match.group(1).strip()
        if "STEP 6" in text:
            parts = text.split("STEP 6")
            if len(parts) > 1:
                raw_prompts = parts[-1].strip()
                cleanup_markers = ["**【作業完了】**", "これ以上の工程は", "引き続きのご承認"]
                for marker in cleanup_markers:
                    if marker in raw_prompts:
                        raw_prompts = raw_prompts.split(marker)[0]
                image_prompts = raw_prompts.strip()
        
        # 2. Content (Step 5/7 - Largest HTML block)
        html_matches = re.findall(r'```html(.*?)```', text, re.DOTALL)
        if not html_matches:
            # Fallback
            html_matches = re.findall(r'```(.*?)```', text, re.DOTALL)
            
        content = ""
        if html_matches:
            content = max(html_matches, key=len).strip()
            content = self._post_process_html(content)
            
        # 3. Parsing for Title/Desc
        title = "タイトル取得失敗"
        description = "ディスクリプション取得失敗"

        title_match = re.search(r'---TITLE_START---(.*?)---TITLE_END---', text, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()

        desc_match = re.search(r'---DESC_START---(.*?)---DESC_END---', text, re.DOTALL)
        if desc_match:
            description = desc_match.group(1).strip()
            
        return {
            "title": title,
            "description": description,
            "content": content,
            "image_prompts": image_prompts
        }

    def _post_process_html(self, html: str) -> str:
        """Replaces custom tags, markdown artifacts, and unwanted classes."""
        import re
        
        replacements = {
            "<numlist>": '<div class="numlist">',
            "</numlist>": '</div>',
            "<normalBox>": '<div class="normalBox">',
            "</normalBox>": '</div>',
            "<flow>": '<div class="flow">',
            "</flow>": '</div>',
            "<qa-box01>": '<div class="qa-box01">',
            "</qa-box01>": '</div>',
        }
        for old, new in replacements.items():
            html = html.replace(old, new)
            
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'<p class="[^"]*">', r'<p>', html)
        html = re.sub(r'(<img\s+[^>]*>)', r'<div class="img-100">\1</div>', html)
        
        return html
