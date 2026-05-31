import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 頁面與基本設定 (開啟手機優化版)
# ==========================================
st.set_page_config(page_title="6月打菇任務台", layout="centered", page_icon="🍄")

# ⚡ LINE 內建瀏覽器空間極致優化 CSS
st.markdown("""
    <style>
    /* 1. 拔除頂部與兩側無用空白 */
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }
    /* 2. 隱藏 Streamlit 雲端自帶的黑線與選單 */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3. 自訂緊湊型文字樣式 */
    .line-title {
        font-size: 14pt !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2px;
        color: #222222;
    }
    .line-progress {
        font-size: 13pt !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 6px;
        color: #FF4B4B;
    }
    /* 4. 壓縮元件之間的間距 */
    .element-container {
        margin-bottom: 0.2rem !important;
    }
    /* 5. 讓提示框更緊湊，省出垂直空間 */
    .stAlert {
        padding: 0.4rem 0.6rem !important;
        margin-bottom: 0.3rem !important;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 10pt !important;
        line-height: 1.3 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 用超省空間的 HTML 渲染標題與進度
st.markdown('<div class="line-title">🍄 6月打菇極簡任務台</div>', unsafe_allow_html=True)

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
            "stage_name": f"第{r}輪【{t['stage']}】", 
            "req_mush": t["req_mush"],
            "pre_tasks": t["pre_tasks"]
        })

# 初始化進度計數器
if "mush_count" not in st.session_state:
    st.session_state.mush_count = 0

st.markdown(f'<div class="line-progress">累計已打： {st.session_state.mush_count} 顆</div>', unsafe_allow_html=True)

# 🛠️ 手機友善大按鈕區 (2×2 緊湊排版，防手震、防誤觸)
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ 增加 1 顆", use_container_width=True):
        st.session_state.mush_count = min(117, st.session_state.mush_count + 1)
    if st.button("➖ 扣除 1 顆", use_container_width=True):
        st.session_state.mush_count = max(0, st.session_state.mush_count - 1)
with col2:
    if st.button("🚀 推進 1 天 (+3)", use_container_width=True):
        st.session_state.mush_count = min(117, st.session_state.mush_count + 3)
    if st.button("🔄 進度歸零", use_container_width=True):
        st.session_state.mush_count = 0

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
        return [("🎉 完賽", "3 輪任務全數消滅！")]

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
                daily_actions.append(f"打 {quota_left} 菇推進 **{current_task['stage_name']}** (剩{mush_left - quota_left}菇)")
                mush_left -= quota_left
                quota_left = 0
                
        date_str = current_date.strftime("%m/%d")
        day_label = "今天" if i == 0 else f"明/後天預報"
        action_str = " ➕ ".join(daily_actions)
        pre_task_str = "、".join(list(daily_pre_tasks))
        
        schedule_list.append({
            "title": f"📍 **{day_label} ({date_str}) 指令**",
            "action": action_str,
            "warning": f"⚠️ **前置必做：** {pre_task_str}"
        })
        current_date += timedelta(days=1)
        
    return schedule_list

# ==========================================
# UI 介面：任務卡片輸出
# ==========================================
tomorrow = datetime.today().date() + timedelta(days=1)
detailed_instructions = get_detailed_schedule(3, st.session_state.mush_count, tomorrow)

# 渲染指令
for idx, item in enumerate(detailed_instructions):
    if isinstance(item, tuple): 
        st.success(item[1])
    else:
        # 第一天（今天）用標準顯示，後續天數用折疊面板收起來，保證首屏不爆掉
        if idx == 0:
            st.markdown(item["title"])
            st.info(f"🍄 {item['action']}")
            st.error(item["warning"])
        else:
            with st.expander(f"🔮 點擊查看 {item['title']}", expanded=False):
                st.info(f"🍄 {item['action']}")
                st.error(item["warning"])
