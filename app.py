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
    .category-header { color: #2E86C1; border-bottom: 2px solid #AED6F1; padding-bottom: 5px; margin-top: 25px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>長照補助資格預估器</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 10 項溫馨題目數據
# ---------------------------------------------------------
questions = {
    "🏠 平常在家動一動": [
        {"id": "a1", "label": "1. 吃飯的能力", "options": ["可以自己拿餐具吃得很乾淨", "要人幫忙夾菜或切細，甚至餵幾口", "沒辦法自己吃，完全要人餵"]},
        {"id": "a2", "label": "2. 洗澡的能力", "options": ["自己洗得很順手", "洗不到背、怕滑倒，要人在旁邊看著或幫忙", "完全沒法自己洗，要人全身幫忙"]},
        {"id": "a3", "label": "3. 大小便控制", "options": ["控制得很好，不會尿濕褲子", "偶爾會來不及趕到廁所", "完全沒辦法控制，需要用尿布"]},
        {"id": "a4", "label": "4. 上廁所的能力", "options": ["可以自己進出廁所、穿脫褲子", "需要扶人或扶扶手，甚至要人幫忙擦屁股", "完全沒法自己上，要在床上使用便盆"]},
        {"id": "a5", "label": "5. 走路與爬樓梯", "options": ["在家走得很穩，還能自己上下樓", "要拿拐杖或扶桌子，爬樓梯很吃力", "沒法上下樓，甚至在家也得坐輪椅"]},
    ],
    "🚌 出門走走與生活": [
        {"id": "b1", "label": "6. 使用電話", "options": ["可以自己找電話簿、撥號與對答", "只會接電話，或只能撥幾個熟悉的號碼", "完全不會用電話了"]},
        {"id": "b2", "label": "7. 處理家務與衣服", "options": ["能自己掃地、洗碗或洗小件衣服", "只能做簡單的收納，粗活沒法做", "完全沒法做家事，都要別人代勞"]},
        {"id": "b3", "label": "8. 外出活動與交通", "options": ["能自己搭公車、捷運或騎車出遠門", "要人陪才敢搭車，或只能在家附近走", "完全沒法自己出門"]},
        {"id": "b4", "label": "9. 服用藥物", "options": ["時間到了會自己拿藥吃，分量也正確", "要人先分裝好，或是提醒才記得吃", "完全沒法自己管藥，常吃錯或忘記"]},
        {"id": "b5", "label": "10. 處理財務", "options": ["去銀行或超商算錢、繳費都沒問題", "小錢還可以，大錢（如去銀行）會糊塗", "現在完全不能讓親屬管錢了"]},
    ]
}

# ---------------------------------------------------------
# 3. 第一步：基本身分
# ---------------------------------------------------------
st.subheader("一、 確定親屬身分")
age = st.slider("親屬年齡預估", 0, 125, 65)

col1, col2 = st.columns(2)
with col1:
    is_aboriginal = st.checkbox("具有原住民身分")
    has_disability_card = st.checkbox("領有身心障礙證明")
with col2:
    is_pac = st.checkbox("急性後期整合照護 (PAC) 對象")
    dementia = st.checkbox("經醫師診斷為失智症者")

# ---------------------------------------------------------
# 4. 第二步：日常生活預估
# ---------------------------------------------------------
st.markdown("---")
st.subheader("二、 日常生活預估 (近一個月)")
placeholder = "--- 請選擇親屬狀況 ---"
user_responses = {}

for category, q_list in questions.items():
    st.markdown(f'<div class="category-header"><h4>{category}</h4></div>', unsafe_allow_html=True)
    for q in q_list:
        user_responses[q["id"]] = st.selectbox(q["label"], [placeholder] + q["options"], key=q["id"])

# ---------------------------------------------------------
# 5. 權重邏輯 (攔截邏輯已加入)
# ---------------------------------------------------------
def calculate_precise_status(responses):
    # --- 1. 身分判定 ---
    id_ok = (age >= 65) or (is_aboriginal and age >= 55) or dementia or has_disability_card or is_pac
    identity_points = 50 if id_ok else min(40, (age / 65) * 40)
    
    # --- 2. 身體狀況判定邏輯 ---
    help_count = 0
    unable_count = 0
    for q_id, val in responses.items():
        for cat in questions.values():
            for item in cat:
                if item["id"] == q_id:
                    idx = item["options"].index(val)
                    if idx == 1: help_count += 1
                    if idx == 2: unable_count += 1
    
    # 2 級門檻判定（1項無法 或 2項協助）
    physical_needed = (help_count >= 2) or (unable_count >= 1)
    
    # --- 3. 身體分數計算 ---
    if physical_needed:
        severity_bonus = min(20, (help_count * 2 + unable_count * 5))
        physical_points = 30 + severity_bonus
    else:
        physical_points = min(25, (help_count * 10)) 
        
    # --- 4. 總分與攔截邏輯 ---
    total_rate = identity_points + physical_points
    
    # 只要有一項不符，強制壓在 80 分以下
    if not id_ok or not physical_needed:
        total_rate = min(79.0, total_rate)

    return total_rate, id_ok, physical_needed

# ---------------------------------------------------------
# 6. 送出結果 (這裡已修正呼叫名稱)
# ---------------------------------------------------------
if st.button("✨ 查看預估結果"):
    if placeholder in user_responses.values():
        st.error("⚠️ 還有預估題目漏掉囉！請填完 10 個項目。")
    else:
        # 【修正點】：函數名稱必須與上面定義的 calculate_precise_status 一致
        total_rate, id_ok, physical_needed = calculate_precise_status(user_responses)
        
        st.markdown(f"""
        <div class="result-box">
            <div style='color: #666; font-size: 1.1rem;'>政府補助資格預估指數</div>
            <div style='font-size: 3.8rem; font-weight: bold; color: #F39800;'>{total_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 邏輯分支一：完全符合
        if id_ok and physical_needed:
            st.success("✅ **預估符合補助資格！**")
            st.write("親屬的身分條件與身體照顧需求皆已達標。建議儘速撥打 **1966** 申請正式評估。")
            st.balloons()
            
        # 邏輯分支二：身分問題
        elif not id_ok and physical_needed:
            st.warning("🟡 **補助預估未達標：身分條件問題**")
            st.write("雖然親屬目前的身體狀況非常需要照顧，但因「年齡或身分證明」尚未符合政府法定補助門檻，故暫時無法申請政府資源。")
            st.info("💡 **好厝邊建議：** 雖然政府暫無補助，但照顧不能等。您可以找UIA好厝邊，為您安排合適的服務廠商。")

        # 邏輯分支三：身體狀況問題
        elif id_ok and not physical_needed:
            st.warning("🟡 **補助預估未達標：身體狀況活動良好**")
            st.write("親屬的身分雖然符合申請資格，但目前「身體自理能力尚佳」，預估失能等級尚未達到政府補助的最低標準 (CMS 2級)。")
            st.info("💡 **好厝邊建議：** 目前親屬健康狀況良好，建議維持規律運動預防失能。若您有接送、輔具或居家改造需求歡迎找好厝邊幫您安排！")
            
        # 邏輯分支四：兩者皆不符
        else:
            st.info("⚪ **補助預估指數較低**")
            st.write("親屬目前身分尚未屆齡，且身體活動狀況良好，暫不符合政府長照補助資格。")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.8rem; color:#888;">💌 UIA好厝邊｜本預估僅供參考，正式結果以政府評估為準。</div>', unsafe_allow_html=True)
