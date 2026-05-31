import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 頁面與基本設定
# ==========================================
st.set_page_config(page_title="6月極限打菇任務台", layout="centered", page_icon="🍄")

st.title("🍄 6月打菇極簡任務台")
st.markdown("不用登入！隨點隨看。請用下方按鈕調整您目前的進度：")

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
# UI 介面：手機版大按鈕進度控制
# ==========================================
# 初始化暫存變數
if "mush_count" not in st.session_state:
    st.session_state.mush_count = 0

st.markdown("---")
st.subheader("⚙️ 目前進度微調")

# 顯示目前巨大的數字
st.markdown(f"<h3 style='text-align: center; color: #FF4B4B;'>目前累計已摧毀： {st.session_state.mush_count} 顆</h3>", unsafe_allow_html=True)

# 手機友善的大按鈕排版
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➖ 扣 1 顆", use_container_width=True):
        st.session_state.mush_count = max(0, st.session_state.mush_count - 1)
with col2:
    if st.button("➕ 加 1 顆", use_container_width=True):
        st.session_state.mush_count = min(117, st.session_state.mush_count + 1)
with col3:
    if st.button("➕ 加 3 顆", use_container_width=True):
        st.session_state.mush_count = min(117, st.session_state.mush_count + 3)
with col4:
    if st.button("🔄 歸零", use_container_width=True):
        st.session_state.mush_count = 0

st.markdown("---")

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
st.subheader("📝 接下來 3 天的行動指令")

tomorrow = datetime.today().date() + timedelta(days=1)
detailed_instructions = get_detailed_schedule(3, st.session_state.mush_count, tomorrow)

for item in detailed_instructions:
    if isinstance(item, tuple): 
        st.success(item[1])
    else:
        with st.container():
            st.markdown(item["title"])
            st.info(f"🍄 **打菇目標：** {item['action']}")
            st.error(item["warning"]) 
            st.markdown("---")
