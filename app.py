import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(page_title="UIA好厝邊-長照補助小幫手", page_icon="🏡", layout="centered")

# --- CSS 樣式優化 ---
st.markdown("""
    <style>
    h1 { color: #F39800 !important; text-align: center; }
    .stSelectbox div[data-baseweb="select"] { border: 1px solid #F39800; }
    .result-box { text-align: center; padding: 20px; border: 2px solid #F39800; border-radius: 20px; margin: 20px 0; }
    .category-header { color: #2E86C1; border-bottom: 2px solid #AED6F1; padding-bottom: 5px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>長照補助資格測評器</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-intro" style="text-align: center;">照顧路上，您辛苦了！<br>跟著好厝邊簡單評估長照 3.0 資格。</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 溫馨的題目清單數據 (您提供的內容)
# ---------------------------------------------------------
questions = {
    "🏠 平常在家動一動": [
        {"id": "a1", "label": "洗澡能自己來嗎？", "options": ["沒問題", "洗不到背或怕滑倒，要人在旁邊", "沒辦法，要人幫忙洗"]},
        {"id": "a2", "label": "起身跟走路還穩嗎？", "options": ["健步如飛", "要扶桌子或是拿拐杖", "要人扶才敢走"]},
        {"id": "a3", "label": "爬一樓樓梯還可以嗎？", "options": ["輕輕鬆鬆", "要扶扶手慢慢爬", "膝蓋沒力爬不動了"]},
    ],
    "🚌 出門走走與生活": [
        {"id": "b1", "label": "自己搭車去遠一點的地方？", "options": ["可以呀", "要人陪才敢去", "完全沒法出遠門"]},
        {"id": "b2", "label": "醫生開的藥會記得吃嗎？", "options": ["準時吃藥", "要人分裝或是提醒才會吃", "常常忘記或吃錯"]},
        {"id": "b3", "label": "去超商買東西算錢順利嗎？", "options": ["算得很清楚", "小錢還可以，大錢會糊塗", "現在都不敢讓他管錢了"]},
    ],
    "💡 最近的心情與記性": [
        {"id": "c1", "label": "最近有沒有變得很愛生氣或疑心？", "options": ["跟以前一樣", "偶爾會情緒不穩", "很常重複問話或是半夜不睡"]}
    ]
}

# ---------------------------------------------------------
# 3. 第一步：基本身分
# ---------------------------------------------------------
st.subheader("一、 確定親屬身分")
age = st.slider("親屬年齡", 0, 125, 65)

col1, col2 = st.columns(2)
with col1:
    is_aboriginal = st.checkbox("具有原住民身分")
    has_disability_card = st.checkbox("領有身心障礙證明")
with col2:
    is_pac = st.checkbox("急性後期整合照護計畫對象")
    dementia = st.checkbox("經醫師診斷為失智症者")

# ---------------------------------------------------------
# 4. 第二步：日常生活評估 (動態生成題目)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("二、 日常生活評估 (近一個月)")
st.info("💡 請根據長輩最近的真實狀況選擇最接近的描述。")

placeholder = "--- 請選擇狀況 ---"
user_responses = {}

for category, q_list in questions.items():
    st.markdown(f'<div class="category-header"><h4>{category}</h4></div>', unsafe_allow_html=True)
    for q in q_list:
        user_responses[q["id"]] = st.selectbox(
            q["label"], 
            [placeholder] + q["options"], 
            key=q["id"]
        )

# ---------------------------------------------------------
# 5. 邏輯運算
# ---------------------------------------------------------
def calculate_3_0_logic(responses, is_pac_status):
    # 判斷身分
    is_group_match = (
        (age >= 65) or 
        (is_aboriginal and age >= 55) or 
        dementia or 
        has_disability_card or 
        is_pac_status
    )
    
    # 計算失能權重 (判定是否選了非第一選項)
    # 我們定義只要不是選第一個「最健康」的選項，就視為有潛在需求
    need_help_count = 0
    for q_id, val in responses.items():
        # 尋找該題目的選項清單
        options_list = []
        for cat in questions.values():
            for item in cat:
                if item["id"] == q_id:
                    options_list = item["options"]
        
        # 如果選的不是第一個選項 (index 0)，算入失能權重
        if val != options_list[0]:
            need_help_count += 1

    # 簡單模擬 CMS 分數 (總共 7 題)
    # 這裡將係數稍微調高，因為題目變少了
    z = -3.0 + (need_help_count * 1.2)
    if is_pac_status: z += 1.0 
    
    prob = 1 / (1 + np.exp(-z))
    return is_group_match, prob

# ---------------------------------------------------------
# 6. 送出結果
# ---------------------------------------------------------
if st.button("✨ 點我開始評估"):
    # 檢查是否有未填寫的題目
    if placeholder in user_responses.values():
        st.error("⚠️ 還有題目漏掉囉！請檢查上方是否有尚未選取的下拉選單。")
    else:
        is_match, prob = calculate_3_0_logic(user_responses, is_pac)
        
        st.markdown(f"""
        <div class="result-box">
            <h2>推估媒合度</h2>
            <div style='font-size: 3.5rem; font-weight: bold; color: #F39800;'>{prob*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        is_cms2 = prob >= 0.5
        
        if is_match and is_cms2:
            st.success("✅ **符合長照 3.0 補助資格！**")
            st.write("根據您的初步描述，長輩很有機會申請到政府補助。建議撥打 **1966** 預約照專到府評估。")
            st.balloons()
        elif is_match and not is_cms2:
            st.warning("🟡 **身分符合，但目前失能程度較輕。**")
            st.write("雖然身分符合，但目前的自理能力看起來還不錯。若之後有退化現象，請隨時回來重測。")
        else:
            st.info("⚪ **目前尚未完全符合補助門檻。**")
            st.write("別擔心，您可以持續觀察長輩狀況，或諮詢專業廠商安排預防失能的活動。")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.8rem; color:#888;">💌 UIA好厝邊｜本評估僅供參考，正式結果以政府評估為準。</div>', unsafe_allow_html=True)
