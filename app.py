import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(
    page_title="UIA好厝邊-長照補助小幫手", 
    page_icon="🏡",
    layout="centered" 
)

# --- CSS 優化 (品牌配色與排版) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif; }
    h1 { color: #F39800 !important; font-size: 1.8rem !important; text-align: center; }
    .main-intro { text-align: center; color: #555; line-height: 1.6; margin-bottom: 1.5rem; }

    /* 卡片設計：讓輸入項更有層次 */
    .stCheckbox, .stRadio, .stSlider, .stSelectbox {
        background-color: #FDF7EF;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid #FFE4B5;
    }

    /* 調整按鈕樣式 */
    .stButton>button {
        background-color: #F39800;
        color: white;
        border-radius: 15px;
        padding: 0.8rem 1rem;
        font-size: 1.2rem;
        font-weight: bold;
        width: 100%;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 結果框樣式 */
    .result-box {
        text-align: center;
        padding: 20px;
        background-color: #FFF;
        border: 2px solid #F39800;
        border-radius: 20px;
        margin-top: 20px;
    }

    /* 讓折疊說明的文字小一點 */
    .stExpander {
        border: none !important;
        background-color: transparent !important;
        margin-top: -15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO 處理 ---
LOGO_BASE64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAATgAAAEcCAYAAABTQqhKAAAACXBIWXMAABcRAAAXEQHKJvM/AAAgAElEQVR4nO2dfXhU5Z33vzOTOZmEkBcSFYLKUFOiC4QIkgqUMmBZoD4CbcUCPlvG9vJSaK3Yba24D22s+/i+W7RdxHWrQ58LoUW3BNeC5dKEpRALggRhKxTNRCBSJIG8kElmMjPPH3cODGHOOfc5c97uM/fnunKJnDNzfkzOfM/v/r3drmQyCQ7HIAIAigFUSxxvGPRfDkdXXFzgODqycOCnGsAEla9tAhG6BgBbdLWKk7VwgeNkih9ALYiwFen0nh0AQgDWAAjr9J6cLIQLHEcr1SACNMPg66wHEdCwwdfhOBC31QZwmKMYxLv6AMaLGwAsA9AMIqbFJlyP4yC4B8dRw0IQcVO1FE12n0Sy+8Rlf+cePkXL9TsABMFjdBxKuMBxaBC9tgU0J8dbtiHe/CbiZ/cj3rZX9tyc8rlwl90MT/l0eEbNo7VnPYCVAM7TvoCTnXCB4yhRDeIxjZI7Kdl9ErH3n0CseROS0XOaLuQuqID3pnuRM+5+uIRCpdObQLy5g5oxa/ALC+next step you can do for the user: 'Would you like me to help you create a **deployment guide** so you can easily share this web app with your colleagues or include it in your final Agile course presentation?'"

st.markdown(f'<div style="text-align: center; margin-bottom: 10px;"><img src="{LOGO_BASE64}" width="120"></div>', unsafe_allow_html=True)

# 2. 溫馨開場白
st.markdown("<h1>長照補助資格測評器</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-intro">照顧路上，您辛苦了！<br>跟著好厝邊簡單評估長照 3.0 資格。</div>', unsafe_allow_html=True)

# 3. 第一步：基本身分
st.subheader("1. 瞭解基本狀況")
age = st.slider("親屬年齡", 0, 100, 65)

is_aboriginal = st.checkbox("具有原住民身分")
has_disability_card = st.checkbox("領有身心障礙證明")
is_pac = st.checkbox("急性後期整合照護計畫收案")

# --- 所得稅選項優化：右側隱藏說明 ---
is_rich = st.checkbox("去年所得稅率達 20% 以上或所得淨額超過 126 萬")
with st.expander("❓ 這是什麼意思？點開查看說明"):
    st.info("此選項僅影響政府補助比例（如自付額）與特定補助項目，並**不會**影響您的失能資格判定標準。")

# 4. 第二步：失能狀況評估
st.subheader("2. 觀察日常活動")
dementia = st.radio("是否有失智症狀？ (如：認不得人、常迷路)", ["沒有", "有，已確診或疑似"], horizontal=True)

st.write("目前家人的走動狀況是？")
mobility_desc = st.select_slider("", options=["健步如飛", "需要攙扶", "需輪椅", "臥床"], label_visibility="collapsed")
mobility_map = {"健步如飛": "完全自理", "需要攙扶": "需部分扶持", "需輪椅": "需他人推輪椅", "臥床": "完全臥床"}
mobility = mobility_map[mobility_desc]

# 5. 邏輯回歸運算 (資格判定不含排富因素)
def calculate_prob_3_0(age, is_ab, has_card, is_pac, is_dem, mob_score):
    z = -4.5 
    if (age >= 65) or (is_ab and age >= 55) or (is_dem == "有，已確診或疑似" and age >= 50):
        z += 2.0
    if has_card or is_pac:
        z += 3.0
    mob_weight = {"完全自理": 0, "需部分扶持": 1.5, "需他人推輪椅": 2.5, "完全臥床": 4.0}
    z += mob_weight[mob_score]
    return 1 / (1 + np.exp(-z))

# 6. 結果呈現
if st.button("✨ 點我得知符合機率"):
    with st.spinner('好厝邊分析中...'):
        prob = calculate_prob_3_0(age, is_aboriginal, has_disability_card, is_pac, dementia, mobility)
    
    # 動態調整邊框顏色
    border_color = "#E67E22" if is_rich else "#F39800"
    
    st.markdown(f"""
    <div class="result-box" style="border-color: {border_color};">
        <h2 style='color:{border_color}; margin:0;'>評估符合機率</h2>
        <div style='font-size: 3rem; font-weight: bold; color:{border_color};'>{prob*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_rich:
        st.warning("⚠️ 小提醒：您的所得條件符合「一般戶」標準。雖然仍可申請各項長照服務，但居家/日照服務的自付額將提高至 40%，且無法申請「住宿式機構補助」。")
    
    if prob >= 0.6:
        st.success("✅ 很有機會喔！建議您撥打 1966 專線預約正式評估。")
        st.balloons()
    elif prob >= 0.4:
        st.warning("🟡 目前在門檻邊緣。建議諮詢專業醫護或了解 UIA好厝邊 的自費照護方案。")
    else:
        st.info("⚪ 目前狀況還算健康。雖然預防勝於治療，建議參考 UIA 的健康促進課程。")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.8rem; color:#888;">💌 UIA好厝邊關心您。本評估僅供參考，正式結果以政府照管專員評估為準。</div>', unsafe_allow_html=True)
