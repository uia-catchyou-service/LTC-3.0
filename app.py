import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(page_title="UIA好厝邊-長照補助資格預估器", page_icon="🏡", layout="centered")

# --- CSS 樣式優化 (整合強力修正 Android 掉字問題與橘色標題) ---
st.markdown("""
    <style>
    /* 1. 標題與副標題樣式 */
    h1 { 
        color: #F39800 !important; 
        text-align: center; 
        font-size: clamp(2rem, 8vw, 3.5rem) !important; 
        font-weight: 800 !important;
        line-height: 1.3 !important;
    }
    .sub-title {
        text-align: center; 
        color: #666; 
        line-height: 1.6; 
        font-size: clamp(1rem, 4vw, 1.2rem);
        margin-bottom: 2rem;
    }

    /* 2. 確保選單「外框」高度可以自動長高 */
    div[data-baseweb="select"] > div {
        height: auto !important;
        min-height: 3rem !important;
        padding: 5px 0 !important;
    }

    /* 3. 核心修正：解決選項點開後被截斷成 ... 的問題 (Android 強力修復) */
    div[role="listbox"] ul li div {
        white-space: normal !important; /* 允許自動換行 */
        line-height: 1.5 !important;
        height: auto !important;
        overflow: visible !important;   /* 讓溢出的文字顯示出來 */
        display: block !important;     /* 確保不是彈性盒子導致的單行限制 */
        padding: 10px 5px !important;
        word-break: break-word !important;
    }

    /* 4. 解決選單內容顯示不全與自動換行 */
    [data-testid="stMarkdownContainer"] p {
        white-space: normal !important;
        word-break: break-word !important;
        overflow: visible !important;
    }

    /* 5. 針對 Android 特有的內層容器進行高度釋放 */
    div[data-baseweb="popover"] > div {
        max-height: 550px !important; 
    }
    
    /* 題目標籤文字樣式 */
    .stSelectbox label p { 
        white-space: normal !important; 
        font-weight: 600 !important; 
        font-size: clamp(1rem, 4vw, 1.2rem) !important;
    }

    /* 結果框優化：確保數字不跑掉、維持一行 */
    .result-box {
        text-align: center;
        padding: 20px;
        border: 2px solid #F39800;
        border-radius: 20px;
        margin: 20px 0;
        height: auto !important;
    }

    .result-num {
        /* 關鍵：強制不換行 */
        white-space: nowrap !important; 
        /* 使用 clamp 讓字體有彈性，防止撐破框 */
        font-size: clamp(2.5rem, 12vw, 3.8rem) !important; 
        font-weight: bold !important;
        color: #F39800;
        display: inline-block;
        width: 100%;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 標題與副標題渲染 ---
st.markdown("<h1>長照補助資格預估器</h1>", unsafe_allow_html=True)
st.markdown("""
<div class="sub-title">
    照顧路上，您辛苦了！<br>
    跟著好厝邊簡單預估長照 3.0 補助資格。
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 10 項溫馨題目數據
# ---------------------------------------------------------
questions = {
    "🏠 平常在家動一動": [
        {"id": "a1", "label": "1. 吃飯的能力", "options": ["可以自己拿餐具吃得很乾淨", "要人幫忙夾菜或切細，甚至餵幾口", "無法自己吃，完全要人餵"]},
        {"id": "a2", "label": "2. 洗澡的能力", "options": ["自己洗得很順手", "洗不到背、怕滑倒，要人在旁邊看著或幫忙", "完全無法自己洗，要人全身幫忙"]},
        {"id": "a3", "label": "3. 大小便控制", "options": ["控制得很好，不會尿濕褲子", "偶爾會來不及趕到廁所", "完全沒辦法控制，需要用尿布"]},
        {"id": "a4", "label": "4. 上廁所的能力", "options": ["可以自己進出廁所、穿脫褲子", "需要扶人或扶扶手，以及幫忙擦屁股", "完全無法自己上，要在床上使用便盆"]},
        {"id": "a5", "label": "5. 走路與爬樓梯", "options": ["在家走得很穩，還能自己上下樓", "要拿拐杖或扶桌子，爬樓梯很吃力", "無法上下樓，甚至在家也得坐輪椅"]},
    ],
    "🚌 出門走走與生活": [
        {"id": "b1", "label": "6. 使用電話", "options": ["可以自己用電話撥號與對答", "只會接電話或只能撥幾個熟悉的號碼", "完全不會用電話了"]},
        {"id": "b2", "label": "7. 處理家務與衣服", "options": ["能自己掃地、洗碗或洗小件衣服", "只能做簡單的收納，粗活沒法做", "完全無法做家事，都要別人代勞"]},
        {"id": "b3", "label": "8. 外出活動與交通", "options": ["能自己搭公車、捷運或騎車出遠門", "要人陪才敢搭車，或只能在家附近走", "完全無法自己出門"]},
        {"id": "b4", "label": "9. 服用藥物", "options": ["時間到了會自己拿藥吃，分量也正確", "要人先分裝好或提醒才記得吃", "完全無法自己管藥，常吃錯或忘記"]},
        {"id": "b5", "label": "10. 處理財務", "options": ["去銀行或超商算錢、繳費都沒問題", "小錢還可以，大錢（如去銀行）會糊塗", "完全無法自理錢財了"]},
    ]
}

# ---------------------------------------------------------
# 3. 第一步：基本身分
# ---------------------------------------------------------
st.subheader("一、 確定親屬身分")
age = st.slider("親屬年齡預估", 0, 125, 65)

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
        st.error("⚠️ 還有預估題目漏掉囉！請填完 10 個項目。")
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
            st.balloons()
        elif not id_ok and physical_needed:
            st.warning("🟡 **補助預估未達標：身分條件問題**")
            st.write("雖然親屬目前的身體狀況確實需要照顧，但因「年齡或身分證明」尚未符合政府法定補助門檻，故暫時無法申請政府長照補助。")
            st.info("💡 **好厝邊建議：** 雖然政府暫無補助，但照顧不能等。您可以找UIA好厝邊為您安排合適服務。")
        elif id_ok and not physical_needed:
            st.warning("🟡 **補助預估未達標：身體狀況活動良好**")
            st.write("親屬的身分雖然符合，但目前「身體自理能力尚佳」，預估失能等級尚未達到補助標準 (CMS 2級)。")
            st.info("💡 **好厝邊建議：** 目前親屬健康狀況良好，建議維持規律運動。若有接送、輔具或居家改造需求歡迎找UIA好厝邊協助您安排！")
        else:
            st.info("⚪ **補助預估指數較低**")
            st.write("親屬目前身分尚未屆齡且身體活動狀況良好，暫不符合政府長照補助資格。")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.75rem; color:#888; line-height:1.6;">💌 UIA好厝邊｜本檢測工具（以下簡稱「本工具」）係由「好厝邊」團隊獨立研發，旨在提供使用者初步之長照需求篩檢 。本工具之評估邏輯係 「參考」 衛生福利部公告之 ADLs 與 IADLs 指標，並非官方正式評估量表。預估結果不具備正式醫療或行政法律效力，實際補助資格應以各縣市照管中心之正式評估結果為準。</div>', unsafe_allow_html=True)
