import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(page_title="UIA好厝邊-長照補助資格預估器", page_icon="🏡", layout="centered")

# --- CSS 樣式優化 (整合強力修正 Android 掉字問題與橘色標題) ---
st.markdown("""
    <style>
    /* 標題樣式：橘色、置中、隨螢幕縮放 */
    h1 { 
        color: #F39800 !important; 
        text-align: center !important; 
        font-size: clamp(2rem, 8vw, 3.5rem) !important; 
        font-weight: 800 !important;
        line-height: 1.3 !important;
        margin-bottom: 0.5rem !important;
    }

    /* 副標題樣式：置中、灰色 */
    .sub-title {
        text-align: center !important; 
        color: #666 !important; 
        line-height: 1.6 !important; 
        font-size: clamp(1rem, 4vw, 1.2rem) !important;
        margin-bottom: 2rem !important;
    }

    /* 下拉選單文字基礎換行 */
    .stSelectbox label p, div[data-baseweb="select"] p { 
        white-space: normal !important; 
        word-break: break-word !important;
    }

    /* 結果框優化：確保數字單行呈現 */
    .result-box {
        text-align: center;
        padding: 20px 5px !important;
        border: 2px solid #F39800;
        border-radius: 20px;
        margin: 20px 0;
    }

    .result-num {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: baseline !important;
        white-space: nowrap !important; 
        font-size: clamp(2rem, 10vw, 3rem) !important; 
        font-weight: bold !important;
        color: #F39800;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 標題與副標題渲染 ---
st.markdown("<h1>長照補助資格預估器</h1>", unsafe_allow_html=True)

st.markdown("""
<div class="sub-title">
    只需1分鐘，UIA好厝邊幫您預估是否符合長照補助資格！
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 10 項溫馨題目數據
# ---------------------------------------------------------
questions = {
    "🏠 日常活動": [
        {"id": "a1", "label": "1. 進食", "options": ["可以自己吃", "要有人協助或監督", "全程需要有人餵食"]},
        {"id": "a2", "label": "2. 洗漱", "options": ["可以自己洗澡與洗漱", "要人協助或監督", "全程需要人協助"]},
        {"id": "a3", "label": "3. 大小便控制", "options": ["可以自己控制好", "每周不超過1次失禁", "每周超過2次失禁"]},
        {"id": "a4", "label": "4. 如廁", "options": ["可以自行或透過輔具如廁", "部分過程需人協助才能完成", "需全程有人協助"]},
        {"id": "a5", "label": "5. 行動", "options": ["可以自行或透過助行器前行50公尺", "需人扶持或操作輪椅前行50公尺", "完全依賴他人才能前行"]},
        {"id": "b1", "label": "6. 電話", "options": ["可以自己打電話", "只能接電話", "完全不會使用電話"]},
        {"id": "b2", "label": "7. 家務", "options": ["可以自己做家事", "要人協助才能完成家事", "完全無法做家事"]},
        {"id": "b3", "label": "8. 外出", "options": ["可以自己搭車或出遠門", "要人陪才能搭車", "完全無法自己出門"]},
        {"id": "b4", "label": "9. 服藥", "options": ["可以自己在正確時間用藥", "需有人準備好，但可自行用藥", "完全無法自己用藥"]},
        {"id": "b5", "label": "10. 財務處理", "options": ["可以自己處理錢財", "僅能使用小額支出", "無法自己處理任何金錢"]},
    ]
}

# ---------------------------------------------------------
# 3. 第一步：基本身分
# ---------------------------------------------------------
st.subheader("一、 確定親屬身分")
age = st.slider("親屬年齡", 0, 125, 65)

pac_help_text = """
**PAC 計畫對象包含：**
1. 腦中風
2. 燒燙傷
3. 創傷性神經損傷
4. 脆弱性骨折
5. 心臟衰竭
6. 衰弱高齡病人

**判定方式：**
親屬在急性期出院前，是否有經醫院評估並轉介至合適院所繼續接受「急性後期整合照護」？若有，請勾選。
"""

col1, col2 = st.columns(2)
with col1:
    is_aboriginal = st.checkbox("具有原住民身分")
    has_disability_card = st.checkbox("領有身心障礙證明") 
with col2:
    is_pac = st.checkbox("急性後期整合照護 (PAC) 對象", help=pac_help_text)
    dementia = st.checkbox("經醫師診斷為失智症者")

# ---------------------------------------------------------
# 4. 第二步：日常生活預估
# ---------------------------------------------------------
st.markdown("---")
st.subheader("二、 最近一個月的生活")
placeholder = "--- 請選擇親屬狀況 ---"
user_responses = {}

for category, q_list in questions.items():
    st.markdown(f'<div class="category-header"><h4>{category}</h4></div>', unsafe_allow_html=True)
    for q in q_list:
        user_responses[q["id"]] = st.selectbox(q["label"], [placeholder] + q["options"], key=q["id"])

# ---------------------------------------------------------
# 5. 權重邏輯
# ---------------------------------------------------------
def calculate_precise_status(responses):
    id_ok = (age >= 65) or (is_aboriginal and age >= 55) or dementia or has_disability_card or is_pac
    identity_points = 50 if id_ok else min(40, (age / 65) * 40)
    
    help_count = 0
    unable_count = 0
    for q_id, val in responses.items():
        for cat in questions.values():
            for item in cat:
                if item["id"] == q_id:
                    idx = item["options"].index(val)
                    if idx == 1: help_count += 1
                    if idx == 2: unable_count += 1
    
    current_raw_score = (help_count * 1) + (unable_count * 2)
    physical_needed = (help_count >= 2) or (unable_count >= 1)
    
    if physical_needed:
        bonus = (current_raw_score - 2) * (20 / 18)
        physical_points = 30 + bonus
    else:
        physical_points = current_raw_score * 15 
        
    total_rate = identity_points + physical_points
    if not id_ok or not physical_needed:
        total_rate = min(79.0, total_rate)
    
    total_rate = min(99.0, total_rate)
    return total_rate, id_ok, physical_needed

# ---------------------------------------------------------
# 6. 送出結果
# ---------------------------------------------------------
if st.button("✨ 查看預估結果"):
    if placeholder in user_responses.values():
        st.error("⚠️ 還有題目漏掉囉！請填完所有題目。")
    else:
        total_rate, id_ok, physical_needed = calculate_precise_status(user_responses)
        
        st.markdown(f"""
        <div class="result-box">
            <div style='color: #666; font-size: 1.1rem;'>政府補助資格預估指數</div>
            <div class="result-num">{total_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        if id_ok and physical_needed:
            st.success("✅ **預估符合補助資格！**")
            st.write("親屬的身分條件與身體照顧需求皆已達標。建議可撥打 **長照專線1966** 申請正式評估。")
            st.info("💡 **提醒：** 除了申請政府補助，若您在等待評估的空窗期需要即時照顧相關服務，UIA好厝邊也能協助您。")
        elif not id_ok and physical_needed:
            st.warning("🟡 **補助預估未達標：身分條件問題**")
            st.write("親屬目前的身體狀況確實需要照顧，但「年齡或身分證明」尚未符合政府法定補助門檻。")
            st.info("💡 **建議：** 雖無法申請政府長照補助，不過照顧不能等，讓UIA好厝邊為您安排合適的照顧相關服務。")
        elif id_ok and not physical_needed:
            st.warning("🟡 **補助預估未達標：身體狀況活動良好**")
            st.write("親屬的身分雖符合，但目前「身體自理能力尚佳」，預估失能等級恐未達到補助標準。")
            st.info("💡 **建議：** 目前親屬健康狀況尚佳，建議維持規律運動。若有照顧相關需求歡迎找UIA好厝邊協助您安排！")
        else:
            st.info("⚪ **補助預估指數較低**")
            st.write("親屬目前身分尚未屆齡且身體活動狀況良好，暫不符合政府長照補助資格。")

st.markdown("---")
st.markdown("""
    <div style="text-align: center; line-height: 1.6;">
        <p style="font-size: 0.75rem; color: #888; margin-top: 15px;">
            💌 UIA好厝邊｜本工具係由「好厝邊」團隊獨立研發，旨在提供初步之長照需求篩檢。評估邏輯參考衛福部公告之 ADLs 與 IADLs 指標，非官方正式量表。預估結果不具法律效力，實際補助資格應以各縣市照管中心評估為準。
            政府資源有限，但UIA好厝邊的用心無限。無論預估結果是否符合補助門檻，UIA好厝邊致力於安排最適合的照護相關解決方案。
        </p>
    </div>
    """, unsafe_allow_html=True)
