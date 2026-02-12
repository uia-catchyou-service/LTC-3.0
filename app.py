import streamlit as st
import numpy as np

# 1. 網頁配置：提升行動端體驗
st.set_page_config(
    page_title="UIA好厝邊-長照補助小幫手", 
    page_icon="🏡",
    layout="centered" 
)

# --- 行動端優化 UI/UX CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    html, body, [class*="css"] {
        font-family: "Microsoft JhengHei", sans-serif;
    }

    h1 {
        color: #F39800 !important;
        font-size: 1.8rem !important;
        text-align: center;
        padding-bottom: 0.5rem;
    }
    .main-intro {
        text-align: center;
        color: #555;
        line-height: 1.6;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    .stCheckbox, .stRadio, .stSlider, .stSelectbox {
        background-color: #FDF7EF;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid #FFE4B5;
    }

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
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #D68500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .result-box {
        text-align: center;
        padding: 20px;
        background-color: #FFF;
        border-radius: 20px;
        margin-top: 20px;
        transition: 0.5s;
    }
    
    /* 動態結果框顏色：一般為橘色，稅率高時稍微轉為深橘/溫和棕色 */
    .border-standard { border: 2px solid #F39800; }
    .border-rich { border: 2px solid #D2691E; background-color: #FFF8F0; }

    /* 說明圖示樣式 */
    .info-icon {
        display: inline-block;
        width: 18px;
        height: 18px;
        background-color: #F39800;
        color: white;
        border-radius: 50%;
        text-align: center;
        font-size: 12px;
        line-height: 18px;
        cursor: help;
        margin-left: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO 處理 (Base64) ---
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

# 所得稅選項增加透明度說明
col_rich, col_info = st.columns([0.9, 0.1])
with col_rich:
    is_rich = st.checkbox("去年所得稅率達 20% 以上或所得淨額超過126萬")
with col_info:
    st.markdown('<span class="info-icon" title="此選項僅影響自付額比例與特定補助申請，不影響失能資格判定。">?</span>', unsafe_allow_html=True)

# 4. 第二步：失能狀況評估
st.subheader("2. 觀察日常活動")
dementia = st.radio("是否有失智症狀？ (如：認不得人、常迷路)", ["沒有", "有，已確診或疑似"], horizontal=True)

st.write("目前家人的走動狀況是？")
mobility_desc = st.select_slider(
    "",
    options=["健步如飛", "需要攙扶", "需輪椅", "臥床"],
    label_visibility="collapsed"
)
mobility_map = {"健步如飛": "完全自理", "需要攙扶": "需部分扶持", "需輪椅": "需他人推輪椅", "臥床": "完全臥床"}
mobility = mobility_map[mobility_desc]

# 5. 邏輯回歸運算 (微調：所得稅不再強制拉低符合機率)
def calculate_prob_3_0(age, is_ab, has_card, is_pac, is_dem, mob_score):
    # 基礎機率邏輯回歸判定
    z = -4.5 
    if (age >= 65) or (is_ab and age >= 55) or (is_dem == "有，已確診或疑似" and age >= 50):
        z += 2.0
    if has_card or is_pac:
        z += 3.0
    mob_weight = {"完全自理": 0, "需部分扶持": 1.5, "需輪椅": 2.5, "臥床": 4.0}
    z += mob_weight[mob_score]
    return 1 / (1 + np.exp(-z))

# 6. 結果呈現
st.write("") 
if st.button("✨ 點我得知符合機率"):
    with st.spinner('好厝邊正在分析中...'):
        prob = calculate_prob_3_0(age, is_aboriginal, has_disability_card, is_pac, dementia, mobility)
    
    # 根據稅率切換 CSS 類別
    box_class = "border-rich" if is_rich else "border-standard"
    text_color = "#D2691E" if is_rich else "#F39800"

    # 使用卡標式結果
    st.markdown(f"""
    <div class="result-box {box_class}">
        <h2 style='color:{text_color}; margin:0;'>評估符合機率</h2>
        <div style='font-size: 3rem; font-weight: bold; color:{text_color};'>{prob*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 

    # 小提醒邏輯微調
    if is_rich:
        st.warning("⚠️ 小提醒：您的所得條件符合「一般戶」標準。雖然仍可申請各項長照服務，但居家/日照服務的自付額將提高至 40% 且無法申請「住宿式服務機構使用者補助」。")
    
    if prob >= 0.6:
        st.success("✅ 很有機會喔！不論所得高低，只要評估失能等級達標即可使用服務，建議您撥打 1966 專線預約正式評估。")
        st.balloons()
    elif prob >= 0.4:
        st.warning("🟡 目前在門檻邊緣。建議諮詢專業醫護或了解UIA好厝邊的服務。")
    else:
        st.info("⚪ 目前狀況還算健康。雖然領到補助的機會較低，但預防勝於治療！")

st.markdown("---")
st.markdown('<div style="text-align:center; font-size:0.8rem; color:#888;">💌 UIA好厝邊關心您。本評估僅供參考，正式結果以政府照管專員評估為準。</div>', unsafe_allow_html=True)
