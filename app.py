import streamlit as st
import pandas as pd

# ==========================================
# 頁面與基本設定 (LINE 極致壓縮版)
# ==========================================
st.set_page_config(page_title="6月打菇順序台", layout="centered", page_icon="🍄")

st.markdown("""
    <style>
    .block-container {
        padding-top: 0.4rem !important;
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
        margin-bottom: 4px;
        color: #FF4B4B;
    }
    
    /* 緊湊任務排版 */
    .task-card {
        background-color: #F0F2F6;
        padding: 0.5rem 0.6rem !important;
        border-radius: 4px;
        margin-bottom: 0.4rem !important;
        border-left: 5px solid #1E88E5;
    }
    .block-card {
        background-color: #FFEBEE;
        padding: 0.5rem 0.6rem !important;
        border-radius: 4px;
        margin-bottom: 0.4rem !important;
        border-left: 5px solid #E53935;
    }
    
    .element-container { margin-bottom: 0rem !important; }
    .stButton button { min-height: 2.5rem !important; font-size: 14px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="line-title">🍄 6月活動嚴格線性任務台</div>', unsafe_allow_html=True)

# ==========================================
# 核心資料庫：將每一小步徹底拆解（含無菇阻擋關卡）
# ==========================================
# mush = 該步驟需要的蘑菇數。如果是 0，代表是純粹的前置阻擋關卡。
linear_tasks = [
    {"id": "1-1", "mush": 0, "text": "走 1000 步"},
    {"id": "1-2", "mush": 0, "text": "培育 2 隻皮克敏"},
    {"id": "1-3", "mush": 0, "text": "完成 2 個探險"},
    {"id": "1-4", "mush": 2, "text": "種植 1000 朵花"},
    
    {"id": "2-1", "mush": 0, "text": "走 2000 步"},
    {"id": "2-2", "mush": 2, "text": "種植 1000 朵花"},
    {"id": "2-3", "mush": 3, "text": "培育 3 隻皮克敏"},
    {"id": "2-4", "mush": 4, "text": "種植 500 朵風鈴草"},
    
    {"id": "3-1", "mush": 0, "text": "走 2000 步 + 完成 2 個探險"},
    {"id": "3-2", "mush": 3, "text": "種植 1500 朵白色鳶尾花"},
    {"id": "3-3", "mush": 4, "text": "種植 1500 朵紅色鳶尾花"},
    {"id": "3-4", "mush": 5, "text": "種植 1500 朵黃色鳶尾花 + 種植 2000 朵紅色風鈴草"},
    
    {"id": "4-1", "mush": 3, "text": "完成 3 個探險"},
    {"id": "4-2", "mush": 4, "text": "種植 2000 朵白色風鈴草"},
    {"id": "4-3", "mush": 4, "text": "種植 2000 朵黃色風鈴草 + 種植 1000 朵藍色鳶尾花"},
    {"id": "4-4", "mush": 5, "text": "種植 2000 朵紅色風鈴草 + 種植 2500 朵鳶尾花(不限色)"},
]

# 展開為 3 輪完整流水線
all_steps = []
for r in range(1, 4):
    for t in linear_tasks:
        all_steps.append({
            "stage_label": f"第{r}輪 STAGE {t['id']}",
            "mush_req": t["mush"],
            "task_text": t["text"]
        })

if "mush_count" not in st.session_state:
    st.session_state.mush_count = 0

st.markdown(f'<div class="line-progress">累計已打： {st.session_state.mush_count} 顆</div>', unsafe_allow_html=True)

# 🛠️ 絕不跑版的雙按鈕
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ 增加 1 顆", use_container_width=True):
        st.session_state.mush_count = min(117, st.session_state.mush_count + 1)
with col2:
    if st.button("➖ 扣除 1 顆", use_container_width=True):
        st.session_state.mush_count = max(0, st.session_state.mush_count - 1)

# ==========================================
# 線性進度推算演算法
# ==========================================
mush_remaining = st.session_state.mush_count
current_step_idx = 0
current_step_mush_done = 0

# 用目前累計的蘑菇數，去扣除線性關卡
while current_step_idx < len(all_steps) and mush_remaining > 0:
    step = all_steps[current_step_idx]
    if step["mush_req"] == 0:
        # 純任務關卡不消耗蘑菇計數，直接遞進
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
# 輸出當前的執行清單 (預測接下來 3 顆菇的額度流向)
# ==========================================
st.markdown("---")

if current_step_idx >= len(all_steps):
    st.success("🎉 3 輪任務全數消滅！")
else:
    st.markdown("**📢 您目前的應做順序清單：**")
    
    projected_quota = 3  # 以今日 3 次免費額度來規劃
    idx = current_step_idx
    mush_done_in_step = current_step_mush_done
    action_counter = 1
    
    while idx < len(all_steps) and projected_quota > 0:
        step = all_steps[idx]
        
        if step["mush_req"] == 0:
            # 紅色卡片：代表純任務阻擋，絕對不能打菇
            st.markdown(f"""
                <div class="block-card">
                    <b>任務({action_counter})： {step['stage_label']}</b><br>
                    🛑 <b>純任務阻擋！此時絕對不可打菇（打了不算進度）</b><br>
                    👉 必須先單獨解完：{step['task_text']}
                </div>
            """, unsafe_allow_html=True)
            idx += 1
        else:
            req_left = step["mush_req"] - mush_done_in_step
            
            if req_left <= projected_quota:
                # 藍色卡片：可以打菇
                st.markdown(f"""
                    <div class="task-card">
                        <b>任務({action_counter})： {step['stage_label']}</b><br>
                        🍄 需打 <b>{req_left}</b> 顆蘑菇解完<br>
                        👉 同時需完成：{step['task_text']}
                    </div>
                """, unsafe_allow_html=True)
                projected_quota -= req_left
                idx += 1
                mush_done_in_step = 0
            else:
                st.markdown(f"""
                    <div class="task-card">
                        <b>任務({action_counter})： {step['stage_label']}</b><br>
                        🍄 需打 <b>{projected_quota}</b> 顆蘑菇推進 (該關還剩 {req_left - projected_quota} 菇)<br>
                        👉 同時需完成：{step['task_text']}
                    </div>
                """, unsafe_allow_html=True)
                projected_quota = 0
                
        action_counter += 1
