import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 頁面與基本設定 (LINE 極致壓縮版)
# ==========================================
st.set_page_config(page_title="6月打菇順序台", layout="centered", page_icon="🍄")

st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    #MainMenu, header, footer {visibility: hidden;}
    
    .line-title {
        font-size: 14pt !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
        color: #222222;
    }
    .line-progress {
        font-size: 14pt !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 8px;
        color: #FF4B4B;
    }
    .element-container { margin-bottom: 0rem !important; }
    .stButton button { min-height: 2.5rem !important; font-size: 14pt !important; }
    
    /* 自訂清單樣式 */
    .day-title {
        font-size: 12pt;
        font-weight: bold;
        color: #1E88E5;
        margin-top: 10px;
        margin-bottom: 4px;
        border-bottom: 1px solid #E0E0E0;
        padding-bottom: 2px;
    }
    .task-line {
        font-size: 11pt;
        line-height: 1.5;
        margin-bottom: 2px;
        color: #333333;
    }
    .task-line-mush {
        font-size: 11pt;
        line-height: 1.5;
        margin-bottom: 2px;
        color: #D32F2F;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="line-title">🍄 6月打菇順序台</div>', unsafe_allow_html=True)

# ==========================================
# 核心資料庫：徹底拆解所有線性任務
# ==========================================
linear_tasks = [
    {"id": "1-1", "mush": 0, "text": "走1000步"},
    {"id": "1-2", "mush": 0, "text": "培育2隻皮克敏"},
    {"id": "1-3", "mush": 0, "text": "完成2個探險"},
    {"id": "1-4", "mush": 2, "text": "種植1000朵花"},
    
    {"id": "2-1", "mush": 0, "text": "走2000步"},
    {"id": "2-2", "mush": 2, "text": "種植1000朵花"},
    {"id": "2-3", "mush": 3, "text": "培育3隻皮克敏"},
    {"id": "2-4", "mush": 4, "text": "種植500朵風鈴草"},
    
    {"id": "3-1", "mush": 0, "text": "走2000步 + 完成2個探險"},
    {"id": "3-2", "mush": 3, "text": "種植1500朵白鳶尾花"},
    {"id": "3-3", "mush": 4, "text": "種植1500朵紅鳶尾花"},
    {"id": "3-4", "mush": 5, "text": "種植1500朵黃鳶尾花 + 2000朵紅風鈴草"},
    
    {"id": "4-1", "mush": 3, "text": "完成3個探險"},
    {"id": "4-2", "mush": 4, "text": "種植2000朵白風鈴草"},
    {"id": "4-3", "mush": 4, "text": "種植2000朵黃風鈴草 + 1000朵藍鳶尾花"},
    {"id": "4-4", "mush": 5, "text": "種植2000朵紅風鈴草 + 2500朵鳶尾花(不限色)"},
]

all_steps = []
for r in range(1, 4):
    for t in linear_tasks:
        all_steps.append({
            "stage_label": f"第{r}輪 {t['id']}",
            "mush_req": t["mush"],
            "task_text": t["text"]
        })

if "mush_count" not in st.session_state:
    st.session_state.mush_count = 0

st.markdown(f'<div class="line-progress">累計已打： {st.session_state.mush_count} 顆</div>', unsafe_allow_html=True)

# 🛠️ 極簡雙按鈕
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ 加 1 顆", use_container_width=True):
        st.session_state.mush_count = min(117, st.session_state.mush_count + 1)
with col2:
    if st.button("➖ 扣 1 顆", use_container_width=True):
        st.session_state.mush_count = max(0, st.session_state.mush_count - 1)

# ==========================================
# 演算法：定位目前進度，並往後推算直到破關
# ==========================================
mush_remaining = st.session_state.mush_count
current_step_idx = 0
current_step_mush_done = 0

while current_step_idx < len(all_steps) and mush_remaining > 0:
    step = all_steps[current_step_idx]
    if step["mush_req"] == 0:
        current_step_idx += 1
    else:
        req = step["mush_req"]
        if mush_remaining >= req:
            mush_remaining -= req
            current_step_idx += 1
        else:
            current_step_mush_done = mush_remaining
            mush_remaining = 0
            break

# ==========================================
# 輸出連續日期的列表 (直到所有任務結束)
# ==========================================
if current_step_idx >= len(all_steps):
    st.success("🎉 3 輪任務已全數完成！")
else:
    current_date = datetime.today().date() + timedelta(days=1)
    idx = current_step_idx
    mush_done_in_step = current_step_mush_done
    day = 0
    
    # 只要還有任務沒解完，就會繼續列出每一天
    while idx < len(all_steps):
        daily_quota = 3
        action_counter = 1
        day_html = f'<div class="day-title">📍 第 {day+1} 天 ({current_date.strftime("%m/%d")})</div>'
        
        while daily_quota > 0 and idx < len(all_steps):
            step = all_steps[idx]
            
            if step["mush_req"] == 0:
                day_html += f'<div class="task-line">({action_counter}) {step["stage_label"]}：{step["task_text"]}</div>'
                idx += 1
            else:
                req_left = step["mush_req"] - mush_done_in_step
                
                if req_left <= daily_quota:
                    day_html += f'<div class="task-line-mush">({action_counter}) {step["stage_label"]}：打菇 {req_left} 次和解任務 ({step["task_text"]})</div>'
                    daily_quota -= req_left
                    idx += 1
                    mush_done_in_step = 0
                else:
                    day_html += f'<div class="task-line-mush">({action_counter}) {step["stage_label"]}：打菇 {daily_quota} 次和解任務 ({step["task_text"]}) ➔ 尚缺 {req_left - daily_quota} 次</div>'
                    mush_done_in_step += daily_quota
                    daily_quota = 0
            
            action_counter += 1
            
        st.markdown(day_html, unsafe_allow_html=True)
        current_date += timedelta(days=1)
        day += 1
