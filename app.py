import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 頁面與基本設定 (極簡雙按鈕版)
# ==========================================
st.set_page_config(page_title="6月打菇任務台", layout="centered", page_icon="🍄")

st.markdown("""
    <style>
    /* 拔除外圍空白，極致壓縮上下空間 */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    #MainMenu, header, footer {visibility: hidden;}
    
    /* 標題與進度樣式 */
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
        margin-bottom: 6px;
        color: #FF4B4B;
    }
    
    /* 任務框與文字緊湊化 */
    .stAlert {
        padding: 0.5rem 0.6rem !important;
        margin-bottom: 0.4rem !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 11pt !important;
        line-height: 1.4 !important;
        margin-bottom: 0 !important;
    }
    
    /* 按鈕稍微加高方便點擊 */
    .stButton button { min-height: 2.5rem !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="line-title">🍄 6月打菇任務台</div>', unsafe_allow_html=True)

# ==========================================
# 核心資料庫 (嚴格順序標示)
# ==========================================
task_db = [
    {"stage": "1-4", "req_mush": 2, "pre_tasks": "先解：①走1000步 ➔ ②培育2隻 ➔ ③完成2探險 ➔ ④種1000花 (此階才可打菇)"},
    {"stage": "2-2", "req_mush": 2, "pre_tasks": "先解：①走2000步 ➔ ②種1000花 (此階才可打菇)"},
    {"stage": "2-3", "req_mush": 3, "pre_tasks": "本階並行：培育3隻皮克敏"},
    {"stage": "2-4", "req_mush": 4, "pre_tasks": "本階並行：種植500朵風鈴草"},
    {"stage": "3-2", "req_mush": 3, "pre_tasks": "先解：①走2000步+2探險 ➔ ②種1500白鳶尾花 (此階才可打菇)"},
    {"stage": "3-3", "req_mush": 4, "pre_tasks": "本階並行：種植1500朵紅鳶尾花"},
    {"stage": "3-4", "req_mush": 5, "pre_tasks": "本階並行：種1500黃鳶尾花 + 2000紅風鈴草"},
    {"stage": "4-1", "req_mush": 3, "pre_tasks": "本階並行：完成3個探險"},
    {"stage": "4-2", "req_mush": 4, "pre_tasks": "本階並行：種植2000朵白風鈴草"},
    {"stage": "4-3", "req_mush": 4, "pre_tasks": "本階並行：種2000黃風鈴草 + 1000藍鳶尾花"},
    {"stage": "4-4", "req_mush": 5, "pre_tasks": "本階並行：種2000紅風鈴草 + 2500鳶尾花(不限色)"},
]

all_tasks = []
for r in range(1, 4):
    for t in task_db:
        all_tasks.append({
            "stage_name": f"第{r}輪 【{t['stage']}】", 
            "req_mush": t["req_mush"],
            "pre_tasks": t["pre_tasks"]
        })

if "mush_count" not in st.session_state:
    st.session_state.mush_count = 0

st.markdown(f'<div class="line-progress">累計已打： {st.session_state.mush_count} 顆</div>', unsafe_allow_html=True)

# 🛠️ 只有 +1 和 -1 的雙按鈕排版 (保證不斷行)
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ 增加 1 顆", use_container_width=True):
        st.session_state.mush_count = min(117, st.session_state.mush_count + 1)
with col2:
    if st.button("➖ 扣除 1 顆", use_container_width=True):
        st.session_state.mush_count = max(0, st.session_state.mush_count - 1)

# ==========================================
# 演算法：條理分明的任務清單
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
        return [("🎉 完賽", ["3 輪任務全數消滅！"])]

    schedule_list = []
    current_date = start_date
    
    for i in range(3):
        quota_left = daily_quota
        daily_actions = []
        action_counter = 1
        
        while quota_left > 0 and task_idx < len(all_tasks):
            current_task = all_tasks[task_idx]
            pre_tasks = current_task["pre_tasks"]
            
            if mush_left <= quota_left:
                daily_actions.append(f"**任務( {action_counter} )： {current_task['stage_name']}** ➔ 打 **{mush_left}** 菇解完\n\n*(確認進度：{pre_tasks})*")
                quota_left -= mush_left
                task_idx += 1
                if task_idx < len(all_tasks):
                    mush_left = all_tasks[task_idx]["req_mush"]
            else:
                daily_actions.append(f"**任務( {action_counter} )： {current_task['stage_name']}** ➔ 打 **{quota_left}** 菇推進\n\n*(確認進度：{pre_tasks})*")
                mush_left -= quota_left
                quota_left = 0
                
            action_counter += 1
                
        date_str = current_date.strftime("%m/%d")
        day_label = "今天" if i == 0 else f"明/後天"
        
        schedule_list.append({
            "title": f"📍 **{day_label} ({date_str})**",
            "actions": daily_actions
        })
        current_date += timedelta(days=1)
        
    return schedule_list

# ==========================================
# UI 介面：任務清單輸出
# ==========================================
st.markdown("---")
tomorrow = datetime.today().date() + timedelta(days=1)
detailed_instructions = get_detailed_schedule(3, st.session_state.mush_count, tomorrow)

for idx, item in enumerate(detailed_instructions):
    if isinstance(item, tuple): 
        st.success(item[1][0])
    else:
        if idx == 0:
            st.markdown(item["title"])
            for action_text in item["actions"]:
                st.info(action_text)
        else:
            with st.expander(f"🔮 查看 {item['title']}", expanded=False):
                for action_text in item["actions"]:
                    st.info(action_text)
