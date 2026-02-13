import argparse
import sys
import time
import os
from dotenv import load_dotenv
from config_manager import load_sites_config, get_gemini_api_key, load_sheets_credentials
from sheet_handler import SheetHandler
from wp_handler import WPHandler
from ai_handler import AIHandler

# Headers (Reference)
HEADERS = ["Status", "MainKW", "SubKW1", "SubKW2", "Goal", "SiteName", "Slug", "DraftURL", "ImagePrompts"]

def process_batch(api_key, sheet_url, sheet_name=None, dry_run=False, log_callback=print, creds_dict=None, manual_prompts=None, manual_common_rules=None):
    """
    Core processing logic, reusable by CLI and Web App.
    log_callback: function to handle log messages (default: print)
    manual_prompts: Dict of prompts (from local config) to override Sheet prompts.
    manual_common_rules: String of common rules (from local config) to override.
    """
    
    # 1. Config Loading (Sites)
    # 1. Config Loading (Sites)
    sites_config = load_sites_config()
    # LOAD CREDS (Dict or Path)
    creds_resource = load_sheets_credentials()
    
    if not sites_config:
        log_callback("Warning: No config/sites.json found or empty. WordPress submission will be skipped.")
        sites_config = {}
    
    if not creds_resource:
        log_callback("Error: No Google Sheets credentials found (checked secrets and service_account.json).")
        return

    # 2. Handlers Init
    log_callback("Initializing handlers...")
    try:
        # Check if creds is dict (from secrets) or path (from file)
        if isinstance(creds_resource, dict):
            sheet = SheetHandler(credentials_dict=creds_resource)
        else:
            sheet = SheetHandler(credentials_path=creds_resource)
            
        sheet.connect(sheet_url, sheet_name)
    except Exception as e:
        log_callback(f"Failed to connect to sheet: {e}")
        return
    
    # Prompt Cache
    prompt_cache = {}

    # 3. Process Loop
    log_callback("Fetching pending tasks...")
    tasks = sheet.get_pending_tasks()
    log_callback(f"Found {len(tasks)} pending tasks.")

    for task in tasks:
        row_idx = task.get("row_index")
        main_kw = task.get("MainKW")
        site_name = task.get("SiteName")
        article_type = task.get("ArticleType", "Default") # Default to "Default" tab if empty
        
        if not main_kw:
            log_callback(f"Skipping row {row_idx}: No MainKW.")
            continue

        if not article_type:
            article_type = "Default"
            
        log_callback(f"\nProcessing Row {row_idx}: {main_kw} (Site: {site_name}, Type: {article_type})")
        
        # Load Prompt Definitions (Cached)
        if article_type in prompt_cache:
            prompt_dict = prompt_cache[article_type]
        else:
            # Check for Manual Prompts (Local Config)
            if manual_prompts and article_type in manual_prompts:
                 log_callback(f"Loading '{article_type}' prompts from Local Config...")
                 prompt_dict = manual_prompts[article_type]
            else:
                 # Fallback to Sheet
                 log_callback(f"Loading prompts for type '{article_type}' from Sheet...")
                 prompt_dict = sheet.get_prompts_from_tab(article_type)

            if not prompt_dict:
                log_callback(f"Error: Prompt tab '{article_type}' not found or empty. Skipping.")
                continue
            prompt_cache[article_type] = prompt_dict

        # Load Instructions (Base/Common Rules)
        instruction_text = ""
        
        # 1a. Manual Common Rules (Local Config Override)
        if manual_common_rules:
            instruction_text += manual_common_rules + "\n\n"
        else:
            # 1b. Local common_rules.md
            common_rules_path = "instructions/common_rules.md"
            if os.path.exists(common_rules_path):
                 with open(common_rules_path, 'r', encoding='utf-8') as f:
                     instruction_text += f.read() + "\n\n"
            
            # 2. Sheet "Common Rules" Tab (共通ルール)
            # Only load if NO manual common rules provided? Or append?
            # Let's append to be safe, or skip if manual is intended to replace.
            # Usually manual replaces file+sheet combo.
            if not manual_common_rules:
                sheet_rules = sheet.get_common_rules("共通ルール")
                if sheet_rules:
                    log_callback("Loaded additional rules from '共通ルール' tab.")
                    instruction_text += "\n\n" + sheet_rules + "\n\n"

        # Site Specific Parts
        parts_file = ""
        if site_name == "麻布十番":
            parts_file = "instructions/parts_azabu.md"
        
        if parts_file and os.path.exists(parts_file):
            log_callback(f"Loading parts list from {parts_file}...")
            with open(parts_file, 'r', encoding='utf-8') as f:
                instruction_text += f.read()
        
        # Re-initialize AI Handler with combined text
        # Gemini Only Mode (Vertex removed per user request)
        ai = AIHandler(api_key, instruction_text=instruction_text)

        # 3a. AI Generation
        sub_kws = f"{task.get('SubKW1', '')}, {task.get('SubKW2', '')}"
        goal = task.get("Goal", "検索意図を満たし、成約につなげる")
        slug = task.get("Slug", "article") # Get slug or default
        
        if dry_run:
            log_callback("[DRY RUN] Would generate article via Gemini...")
            generated = {
                "title": f"Test Title for {main_kw}", 
                "description": "Test Description",
                "content": "Test <img src='test.jpg'> Content", 
                "image_prompts": "Test Prompts"
            }
            time.sleep(1)
        else:
            # Load Mappings (if available)
            mappings = prompt_dict.get("mappings", {})

            # Status Update Callback
            def status_updater(msg):
                log_callback(f"Status Update: {msg}")
                try:
                    sheet.update_status(row_idx, msg)
                except Exception as e:
                    log_callback(f"Failed to update sheet status: {e}")

            # Track mapped columns to avoid overwriting
            mapped_cols_written = set()

            # Step Completion Callback (Real-time Sheet Update)
            def step_listener(step_name, response_text):
                if step_name in mappings:
                    mapping = mappings[step_name]
                    target_col = mapping.get("col")
                    if target_col:
                        log_callback(f"Mapping: Writing {step_name} output to Column {target_col}...")
                        try:
                            if not dry_run:
                                sheet.update_any_cell(row_idx, target_col, response_text)
                                mapped_cols_written.add(target_col)
                            else:
                                log_callback(f"[DRY RUN] Would write to Col {target_col}")
                        except Exception as e:
                            log_callback(f"Failed to write mapped output: {e}")

            status_updater("開始: AI生成中")
            generated = ai.generate_article_flow(
                main_kw, sub_kws, goal, slug, prompt_dict, 
                progress_callback=status_updater,
                step_callback=step_listener
            )
        
        if not generated["content"] and 12 not in mapped_cols_written:
             # Only error if content wasn't written via mapping AND wasn't parsed
             # But if mapping wrote it, generated["content"] might be empty if parse failed, which is fine
             pass
             
        # 3b. WP Submission
        draft_url = ""
        if site_name and site_name in sites_config:
            try:
                wp = WPHandler(sites_config[site_name])
                if dry_run:
                    log_callback(f"[DRY RUN] Would post to {site_name} with slug {task.get('Slug')}")
                    draft_url = "http://example.com/draft-preview"
                else:
                    # Use parsed content for WP (OR should we read from sheet? sticking to parsed for now)
                    # Note: If Mappings utilized, generated["content"] might be empty if regex failed.
                    # Ideally we should trust the generated dict if available, but if empty, maybe user mapped it?
                    # For WP submission, we might need to rely on what was generated.
                    # For now, assuming regex works reasonably well for WP, or user accepts that WP uses parsed.
                    
                    draft_url = wp.post_draft(
                        title=generated.get("title", ""),
                        content=generated.get("content", ""),
                        slug=task.get("Slug", "")
                    )
            except Exception as e:
                log_callback(f"WP Upload failed (continuing to sheet save): {e}")
        else:
            log_callback(f"Site '{site_name}' not configured or empty. Skipping WP upload.")
        
        # 3c. Sheet Update (Final)
        if dry_run:
            log_callback(f"[DRY RUN] Final Update for Row {row_idx}.")
        else:
            # 1. Update Status (Always)
            try:
                sheet.update_status(row_idx, "完了")
            except: pass
            
            # 2. Update Draft URL (Column 8 - H)
            try:
                sheet.update_any_cell(row_idx, 8, draft_url)
            except: pass
            
            # 3. Update other columns ONLY IF not mapped
            # Column 9 (I): Image Prompts
            if 9 not in mapped_cols_written and generated.get("image_prompts"):
                try: sheet.update_any_cell(row_idx, 9, generated["image_prompts"])
                except: pass

            # Column 10 (J): Title
            if 10 not in mapped_cols_written and generated.get("title"):
                try: sheet.update_any_cell(row_idx, 10, generated["title"])
                except: pass

            # Column 11 (K): Description
            if 11 not in mapped_cols_written and generated.get("description"):
                try: sheet.update_any_cell(row_idx, 11, generated["description"])
                except: pass
                
            # Column 12 (L): Content
            if 12 not in mapped_cols_written and generated.get("content"):
                try: sheet.update_any_cell(row_idx, 12, generated["content"])
                except: pass

            log_callback(f"Updated Sheet Row {row_idx} (Status: 完了).")

    log_callback("\nAll tasks processed.")

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Article Automation Tool")
    parser.add_argument("--dry-run", action="store_true", help="Run without sending to API or writing to Sheet")
    parser.add_argument("--sheet-url", type=str, required=True, help="URL of the Google Sheet")
    parser.add_argument("--sheet-name", type=str, help="Name of the worksheet (optional)")
    args = parser.parse_args()

    api_key = get_gemini_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY env var not set.")
        return

    process_batch(
        api_key=api_key,
        sheet_url=args.sheet_url,
        sheet_name=args.sheet_name,
        dry_run=args.dry_run,
        log_callback=print
    )

if __name__ == "__main__":
    main()
