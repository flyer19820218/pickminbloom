import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 頁面與基本設定
# ==========================================
st.set_page_config(page_title="6月極限打菇系統 (雙人版)", layout="centered", page_icon="🍄")

st.title("🍄 6月極限打菇系統 (含完整任務)")
st.markdown("內建多帳號進度分離，並整合所有步數/種花前置任務，防呆防錯。")

# ==========================================
# 核心資料庫：6月完整任務表 (包含所有雜項)
# ==========================================
# req_mush = 需要打的蘑菇數量
# pre_tasks = 打蘑菇前/同時必須完成的其他任務
task_db = [
    # STAGE 1
    {"stage": "1-4", "req_mush": 2, "pre_tasks": ["走 1000 步", "培育 2 隻皮克敏", "完成 2 個探險", "種植 1000 朵花"]},
    # STAGE 2
    {"stage": "2-2", "req_mush": 2, "pre_tasks": ["走 2000 步", "種植 1000 朵花"]},
    {"stage": "2-3", "req_mush": 3, "pre_tasks": ["培育 3 隻皮克敏"]},
    {"stage": "2-4", "req_mush": 4, "pre_tasks": ["種植 500 朵風鈴草"]},
    # STAGE 3
    {"stage": "3-2", "req_mush": 3, "pre_tasks": ["走 2000 步", "完成 2 個探險", "種植 1500 朵白色鳶尾花"]},
    {"stage": "3-3", "req_mush": 4, "pre_tasks": ["種植 1500 朵紅色鳶尾花"]},
    {"stage": "3-4", "req_mush": 5, "pre_tasks": ["種植 1500 朵黃色鳶尾花", "種植 2000 朵紅色風鈴草"]},
    # STAGE 4
    {"stage": "4-1", "req_mush": 3, "pre_tasks": ["完成 3 個探險"]},
    {"stage": "4-2", "req_mush": 4, "pre_tasks": ["種植 2000 朵白色風鈴草"]},
    {"stage": "4-3", "req_mush": 4, "pre_tasks": ["種植 2000 朵黃色風鈴草", "種植 1000 朵藍色鳶尾花"]},
    {"stage": "4-4", "req_mush": 5, "pre_tasks": ["種植 2000 朵紅色風鈴草", "種植 2500 朵鳶尾花(不限色)"]},
]

# 擴充為 3 輪
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
# 帳號與進度系統 (Session State 模擬資料庫)
# ==========================================
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "指揮官 (老師)": {"mushrooms_destroyed": 0},
        "副官 (太太)": {"mushrooms_destroyed": 0}
    }

with st.sidebar:
    st.header("👤 帳號登入與切換")
    # 切換使用者
    current_user = st.selectbox("請選擇目前操作的帳號：", list(st.session_state.users_db.keys()))
    
    st.markdown("---")
    st.header("⚙️ 進度更新")
    st.write(f"目前操作：**{current_user}**")
    
    # 綁定該使用者的進度
    user_progress = st.number_input(
        "👉 修改『累計已打菇』總數", 
        min_value=0, max_value=117, 
        value=st.session_state.users_db[current_user]["mushrooms_destroyed"], 
        step=1
    )
    # 存檔回模擬資料庫
    st.session_state.users_db[current_user]["mushrooms_destroyed"] = user_progress

# ==========================================
# 演算法：推算未來 3 天的懶人包
# ==========================================
def get_detailed_schedule(daily_quota, total_mushrooms, start_date):
    task_idx = 0
    accumulated = 0
    
    # 尋找目前進度
    for idx, task in enumerate(all_tasks):
        if total_mushrooms >= accumulated + task["req_mush"]:
            accumulated += task["req_mush"]
        else:
            task_idx = idx
            mush_left = task["req_mush"] - (total_mushrooms - accumulated)
            break
            
    if task_idx >= len(all_tasks):
        return [("🎉 恭喜！", "3 輪任務已全數完成！不愧是南屯區最強戰力。")]

    schedule_list = []
    current_date = start_date
    
    # 只顯示未來 3 天，保持畫面乾淨
    for i in range(3):
        quota_left = daily_quota
        daily_actions = []
        daily_pre_tasks = set() # 收集當天需要解的所有前置任務
        
        while quota_left > 0 and task_idx < len(all_tasks):
            current_task = all_tasks[task_idx]
            # 把前置任務加進當天的 To-Do
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
        
        # 組合當天任務
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
st.subheader(f"📝 {current_user} 的行動指令")

# 自動從「明天」開始起算
tomorrow = datetime.today().date() + timedelta(days=1)
user_current_mushrooms = st.session_state.users_db[current_user]["mushrooms_destroyed"]

detailed_instructions = get_detailed_schedule(3, user_current_mushrooms, tomorrow)

# 渲染精緻的 UI 卡片
for item in detailed_instructions:
    if isinstance(item, tuple): # 破關狀態
        st.success(item[1])
    else:
        with st.container():
            st.markdown(item["title"])
            st.info(f"🍄 **打菇目標：** {item['action']}")
            st.error(item["warning"]) # 用紅色框提醒前置任務，絕對不會忘！
            st.markdown("---")
