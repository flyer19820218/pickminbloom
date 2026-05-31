import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ==========================================
# 頁面與基本設定
# ==========================================
st.set_page_config(page_title="6月極限打菇排程", layout="centered", page_icon="🍄")

st.title("🍄 6月動態打菇排程模擬器")
st.markdown("手機適配版：支援動態進度調整，隨時校準任務軌道。")

# ==========================================
# 核心資料與演算法：動態打菇排程
# ==========================================
base_tasks = [
    {"stage": "1-4", "req": 2},
    {"stage": "2-2", "req": 2},
    {"stage": "2-3", "req": 3},
    {"stage": "2-4", "req": 4},
    {"stage": "3-2", "req": 3},
    {"stage": "3-3", "req": 4},
    {"stage": "3-4", "req": 5},
    {"stage": "4-1", "req": 3},
    {"stage": "4-2", "req": 4},
    {"stage": "4-3", "req": 4},
    {"stage": "4-4", "req": 5},
]

# 建立 3 輪的完整任務清單
all_tasks = []
for r in range(1, 4):
    for t in base_tasks:
        all_tasks.append({"round": r, "stage": f"第 {r} 輪 [{t['stage']}]", "req": t["req"]})

def calculate_dynamic_schedule(daily_quota, total_destroyed_so_far, current_date):
    # 1. 計算目前卡在哪個任務
    task_idx = 0
    accumulated = 0
    mushrooms_left_in_current = 0
    
    for idx, task in enumerate(all_tasks):
        if total_destroyed_so_far >= accumulated + task["req"]:
            accumulated += task["req"]
        else:
            task_idx = idx
            mushrooms_left_in_current = task["req"] - (total_destroyed_so_far - accumulated)
            break
            
    # 如果已經全部打完
    if task_idx >= len(all_tasks):
        return pd.DataFrame([{"日期": "N/A", "狀態": "🎉 3 輪任務已全數完成！"}])

    # 2. 從今天開始推算未來的排程
    schedule = []
    end_of_month = datetime(2026, 6, 30).date()
    
    while current_date <= end_of_month and task_idx < len(all_tasks):
        daily_log = []
        quota_left = daily_quota
        
        while quota_left > 0 and task_idx < len(all_tasks):
            if mushrooms_left_in_current <= quota_left:
                daily_log.append(f"打 {mushrooms_left_in_current} 顆解完 {all_tasks[task_idx]['stage']}")
                quota_left -= mushrooms_left_in_current
                task_idx += 1
                if task_idx < len(all_tasks):
                    mushrooms_left_in_current = all_tasks[task_idx]["req"]
            else:
                daily_log.append(f"打 {quota_left} 顆推進 {all_tasks[task_idx]['stage']} (剩 {mushrooms_left_in_current - quota_left} 顆)")
                mushrooms_left_in_current -= quota_left
                quota_left = 0
                
        schedule.append({
            "日期": current_date.strftime("%m/%d"),
            "排程分配": " ➕ ".join(daily_log)
        })
        current_date += timedelta(days=1)
        
    return pd.DataFrame(schedule)

# ==========================================
# 側邊欄設定 (動態參數輸入)
# ==========================================
with st.sidebar:
    st.header("⚙️ 動態校準設定")
    today = st.date_input("今天日期", value=datetime(2026, 6, 1).date())
    daily_quota = st.number_input("今日可用蘑菇額度", min_value=1, max_value=10, value=3)
    
    st.markdown("---")
    st.markdown("### 📊 進度回報")
    st.info("如果不小心多打或少打，直接修改下方的總數，系統會自動重新規劃後續天數。")
    total_destroyed = st.number_input("本月『累計已摧毀』總數", min_value=0, max_value=120, value=0)

# ==========================================
# 主畫面
# ==========================================
# 使用 tabs 讓手機滑動更直覺
tab1, tab2 = st.tabs(["📅 動態排程表", "⏱️ 每日行動 SOP"])

with tab1:
    st.subheader("未來排程推算")
    st.markdown(f"**目前累計：{total_destroyed} 顆** (系統已自動扣除並重算)")
    
    df_schedule = calculate_dynamic_schedule(daily_quota, total_destroyed, today)
    st.dataframe(df_schedule, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("手機版行動檢核表")
    st.markdown("出門在外單手點選，避免遺漏關鍵步驟：")
    
    with st.expander("🌞 階段一：晨跑解鎖 (點擊展開)", expanded=True):
        st.checkbox("確認當下任務需求 (防白打)")
        st.checkbox("完成步數與日常種花")
        st.checkbox("特種兵餵精華 (逼上1心)")
        st.checkbox("出戰部隊頂著花進場")
        
    with st.expander("⚔️ 階段二：日間打菇 (點擊展開)"):
        st.checkbox("確認結算時間 < 12 小時")
        st.checkbox("嚴防跨日 (23:59 前必須結算)")
        st.checkbox("依排程精準消耗額度")
        
    with st.expander("🌙 階段三：夜間散步 (點擊展開)"):
        st.checkbox("催熟巨大花苞")
        st.checkbox("榨取水果換取花蜜")
        st.checkbox("花蜜集中投餵主力部隊")
