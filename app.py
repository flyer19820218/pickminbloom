import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 頁面與基本設定
# ==========================================
st.set_page_config(page_title="6月極限打菇懶人包", layout="centered", page_icon="🍄")

st.title("🍄 6月打菇極簡懶人包")
st.markdown("自動抓取日期，滑桿微調進度，每天照著指令點就對了。")

# ==========================================
# 核心資料與演算法
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

# 建立 3 輪完整清單 (共 117 顆菇)
all_tasks = []
for r in range(1, 4):
    for t in base_tasks:
        all_tasks.append({"round": r, "stage": f"第{r}輪 {t['stage']}", "req": t["req"]})

def get_lazy_schedule(daily_quota, total_destroyed_so_far, current_date):
    task_idx = 0
    accumulated = 0
    
    # 尋找目前進度卡在哪
    for idx, task in enumerate(all_tasks):
        if total_destroyed_so_far >= accumulated + task["req"]:
            accumulated += task["req"]
        else:
            task_idx = idx
            mushrooms_left_in_current = task["req"] - (total_destroyed_so_far - accumulated)
            break
            
    if task_idx >= len(all_tasks):
        return ["🎉 恭喜！3 輪任務已全數完成！"]

    # 推算未來 5 天的懶人包 (不用看太遠，看近 5 天就好)
    schedule_list = []
    
    for i in range(5):
        daily_log = []
        quota_left = daily_quota
        
        while quota_left > 0 and task_idx < len(all_tasks):
            if mushrooms_left_in_current <= quota_left:
                daily_log.append(f"打 {mushrooms_left_in_current} 菇解完【{all_tasks[task_idx]['stage']}】")
                quota_left -= mushrooms_left_in_current
                task_idx += 1
                if task_idx < len(all_tasks):
                    mushrooms_left_in_current = all_tasks[task_idx]["req"]
            else:
                daily_log.append(f"打 {quota_left} 菇推進【{all_tasks[task_idx]['stage']}】(剩{mushrooms_left_in_current - quota_left}菇)")
                mushrooms_left_in_current -= quota_left
                quota_left = 0
                
        # 組裝白話文懶人包
        date_str = current_date.strftime("%m/%d")
        day_label = "今天" if i == 0 else f"第 {i+1} 日"
        action_str = " ➕ ".join(daily_log)
        
        schedule_list.append(f"**{day_label} ({date_str})：** {action_str} ✨ *(記得先解完步數/種花等其他任務)*")
        
        current_date += pd.Timedelta(days=1)
        
    return schedule_list

# ==========================================
# UI 介面：控制台
# ==========================================
st.subheader("⚙️ 進度微調控制台")

# 自動抓取今天日期，也可以手動改
today_date = st.date_input("自動判定今天日期 (可點擊修改)", value=datetime.today().date())

# 滑桿設計：直覺拖拉進度
total_mushrooms = st.slider(
    "👉 目前『累計已摧毀』的蘑菇總數 (進度delay直接滑動調整)", 
    min_value=0, max_value=117, value=0, step=1
)

st.markdown("---")

# ==========================================
# UI 介面：懶人包輸出
# ==========================================
st.subheader("📝 接下來 5 天行動指令")

# 產生懶人包
lazy_instructions = get_lazy_schedule(3, total_mushrooms, today_date)

# 用漂亮的 info 框框顯示
for instruction in lazy_instructions:
    st.info(instruction)

st.markdown("---")
with st.expander("💡 晨跑戰前提醒 (點開看)"):
    st.markdown("""
    1. **看指令再打：** 上面寫打幾顆就打幾顆，嚴格扣在任務上。
    2. **步數/種花優先：** 務必先用每天那 5000 朵的跑量把前置任務解完，蘑菇數量才會計算！
    3. **特殊精華準備：** 打開遊戲先給 13 隻新兵餵好餵滿。
    """)
