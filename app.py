import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 頁面與基本設定
# ==========================================
st.set_page_config(page_title="6月極限打菇系統 (5人戰隊版)", layout="centered", page_icon="🍄")

st.title("🍄 6月極限打菇系統 (5人戰隊版)")
st.markdown("特戰小組集結！各自登入，獨立追蹤進度。")

# ==========================================
# 核心資料庫：6月完整任務表 
# ==========================================
task_db = [
    {"stage": "1-4", "req_mush": 2, "pre_tasks": ["走 1000 步", "培育 2 隻皮克敏", "完成 2 個探險", "種植 1000 朵花"]},
    {"stage": "2-2", "req_mush": 2, "pre_tasks": ["走 2000 步", "種植 1000 朵花"]},
    {"stage": "2-3", "req_mush": 3, "pre_tasks": ["培育 3 隻皮克敏"]},
    {"stage": "2-4", "req_mush": 4, "pre_tasks": ["種植 500 朵風鈴草"]},
    {"stage": "3-2", "req_mush": 3, "pre_tasks": ["走 2000 步", "完成 2 個探險", "種植 1500 朵白色鳶尾花"]},
    {"stage": "3-3", "req_mush": 4, "pre_tasks": ["種植 1500 朵紅色鳶尾花"]},
    {"stage": "3-4", "req_mush": 5, "pre_tasks": ["種植 1500 朵黃色鳶尾花", "種植 2000 朵紅色風鈴草"]},
    {"stage": "4-1", "req_mush": 3, "pre_tasks": ["完成 3 個探險"]},
    {"stage": "4-2", "req_mush": 4, "pre_tasks": ["種植 2000 朵白色風鈴草"]},
    {"stage": "4-3", "req_mush": 4, "pre_tasks": ["種植 2000 朵黃色風鈴草", "種植 1000 朵藍色鳶尾花"]},
    {"stage": "4-4", "req_mush": 5, "pre_tasks": ["種植 2000 朵紅色風鈴草", "種植 2500 朵鳶尾花(不限色)"]},
]

all_tasks = []
for r in range(1, 4):
    for t in task_db:
        all_tasks.append({
            "round": r, 
            "stage_name": f"第{r}輪 【{t['stage']}】", 
            "req_mush": t["req_mush"],
            "pre_tasks": t["pre_tasks"]
        })

# ==========================================
# 帳號與進度系統 (支援 5 人小隊)
# ==========================================
squad_members = ["阿虎", "彥君", "小綠人", "阿芳", "阿原"]

# 初始化暫存資料庫 (做為 Google Sheets 的備用機制)
if "users_db" not in st.session_state:
    st.session_state.users_db = {member: 0 for member in squad_members}

# ---------------------------------------------------------
# 💡 未來串接 Google Sheets 的核心函數 (目前為模擬狀態)
# 當您在 Streamlit Cloud 設定好 secrets 後，可以將這裡解開
# ---------------------------------------------------------
def load_data():
    # 實際運作時，這裡會透過 st.connection("gsheets") 讀取您的 Excel
    # df = conn.read(spreadsheet="您的網址")
    return st.session_state.users_db

def save_data(user, new_progress):
    # 實際運作時，這裡會透過 conn.update() 寫回您的 Excel
    st.session_state.users_db[user] = new_progress

# 載入當前所有人的資料
current_db = load_data()

with st.sidebar:
    st.header("👤 戰隊登入")
    current_user = st.selectbox("請選擇您的代號：", squad_members)
    
    st.markdown("---")
    st.header("⚙️ 回報戰果")
    st.write(f"目前操作兵力：**{current_user}**")
    
    # 讀取該成員目前的進度
    user_progress = st.number_input(
        "👉 修改『累計已摧毀』的蘑菇總數", 
        min_value=0, max_value=117, 
        value=current_db[current_user], 
        step=1
    )
    
    # 如果數字有變動，觸發存檔
    if user_progress != current_db[current_user]:
        save_data(current_user, user_progress)
        st.success("💾 進度已更新！")

# ==========================================
# 演算法：推算未來 3 天的懶人包
# ==========================================
def get_detailed_schedule(daily_quota, total_mushrooms, start_date):
    task_idx = 0
    accumulated = 0
    
    for idx, task in enumerate(all_tasks):
        if total_mushrooms >= accumulated + task["req_mush"]:
            accumulated += task["req_mush"]
        else:
            task_idx = idx
            mush_left = task["req_mush"] - (total_mushrooms - accumulated)
            break
            
    if task_idx >= len(all_tasks):
        return [("🎉 任務全制霸！", "3 輪任務已全數完成！特戰小組可以休息了。")]

    schedule_list = []
    current_date = start_date
    
    for i in range(3):
        quota_left = daily_quota
        daily_actions = []
        daily_pre_tasks = set()
        
        while quota_left > 0 and task_idx < len(all_tasks):
            current_task = all_tasks[task_idx]
            for pt in current_task["pre_tasks"]:
                daily_pre_tasks.add(pt)
                
            if mush_left <= quota_left:
                daily_actions.append(f"打 {mush_left} 菇解完 **{current_task['stage_name']}**")
                quota_left -= mush_left
                task_idx += 1
                if task_idx < len(all_tasks):
                    mush_left = all_tasks[task_idx]["req_mush"]
            else:
                daily_actions.append(f"打 {quota_left} 菇推進 **{current_task['stage_name']}** (還剩{mush_left - quota_left}菇)")
                mush_left -= quota_left
                quota_left = 0
                
        date_str = current_date.strftime("%m/%d")
        day_label = f"第 {i+1} 日"
        action_str = " ➕ ".join(daily_actions)
        pre_task_str = "、".join(list(daily_pre_tasks))
        
        schedule_list.append({
            "title": f"**{day_label} ({date_str}) 指令**",
            "action": action_str,
            "warning": f"⚠️ **進場前必須完成：** {pre_task_str}"
        })
        current_date += timedelta(days=1)
        
    return schedule_list

# ==========================================
# UI 介面：主畫面輸出
# ==========================================
st.subheader(f"📝 {current_user} 的專屬行動指令")

tomorrow = datetime.today().date() + timedelta(days=1)
user_current_mushrooms = current_db[current_user]

detailed_instructions = get_detailed_schedule(3, user_current_mushrooms, tomorrow)

for item in detailed_instructions:
    if isinstance(item, tuple): 
        st.success(item[1])
    else:
        with st.container():
            st.markdown(item["title"])
            st.info(f"🍄 **打菇目標：** {item['action']}")
            st.error(item["warning"]) 
            st.markdown("---")
