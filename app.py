import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(page_title="長照補助資格小幫手", page_icon="🏡")

# --- 品牌風格設定 (CSS 強制自定義橘色) ---
st.markdown("""
    <style>
    /* 標題與標籤顏色 */
    .main h1 { color: #F39800; }
    .stButton>button {
        background-color: #F39800;
        color: white;
        border-radius: 20px;
        border: none;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #D68500;
        color: white;
    }
    /* 強調文字顏色 */
    .orange-text { color: #F39800; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 溫馨開場白
st.markdown('<h1 style="text-align: center; 🏡UIA好厝邊</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">長照資格預測</h3>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666;">
照顧路上，您辛苦了！不知道現在的狀況能申請政府補助嗎？<br>
跟著小幫手回答幾個問題，幫您對照 <b>長照 3.0</b> 標準進行初步評估。
</div>
""", unsafe_allow_html=True)

st.divider()

# 3. 第一步：基本身分
st.subheader("1. 聊聊親屬狀況")
col1, col2 = st.columns(2)

with col1:
    age = st.slider("1. 親屬今年幾歲了呢？", 0, 100, 65)
    is_aboriginal = st.checkbox("具有原住民身分")
    has_disability_card = st.checkbox("領有身心障礙證明")

with col2:
    is_pac = st.checkbox("急性後期整合照護對象")
    # 長照 3.0 排富條款
    is_rich = st.checkbox("去年所得稅率達 20% 以上")

# 4. 第二步：失能狀況評估
st.subheader("2. 平時日常活動")
dementia = st.radio("家人是否有失智症狀？ (如：常忘記回家的路、認不得人)", ["沒有", "有，已確診或疑似"], horizontal=True)

mobility_desc = st.select_slider(
    "目前家人的走動狀況是？",
    options=["健步如飛", "需要人家扶一下", "要坐輪椅才能移動", "大部分時間都躺在床上"]
)
mobility_map = {"健步如飛": "完全自理", "需要人家扶一下": "需部分扶持", "要坐輪椅才能移動": "需他人推輪椅", "大部分時間都躺在床上": "完全臥床"}
mobility = mobility_map[mobility_desc]

# 5. 邏輯回歸核心運算
def calculate_prob_3_0(age, is_ab, has_card, is_pac, is_dem, mob_score, is_rich):
    if is_rich: return 0.05  # 排富條款
    z = -4.5 
    if (age >= 65) or (is_ab and age >= 55) or (is_dem == "有，已確診或疑似" and age >= 50):
        z += 2.0
    if has_card or is_pac:
        z += 3.0
    mob_weight = {"完全自理": 0, "需部分扶持": 1.5, "需他人推輪椅": 2.5, "完全臥床": 4.0}
    z += mob_weight[mob_score]
    return 1 / (1 + np.exp(-z))

# 6. 結果呈現
st.divider()
if st.button("✨ 點我開始評估"):
    with st.spinner('小幫手正在分析中...'):
        prob = calculate_prob_3_0(age, is_aboriginal, has_disability_card, is_pac, dementia, mobility, is_rich)
    
    st.markdown(f'### 🎯 AI 評估結果：符合機率約 <span class="orange-text">{prob*100:.1f}%</span>', unsafe_allow_html=True)
    
    
    
    if is_rich:
        st.error("⚠️ **小提醒：** 偵測到家人經濟狀況較優渥，屬於「排富族群」，政府補助將受限。")
    elif prob >= 0.6:
        st.success("✅ **很有機會喔！** 建議您現在就撥打 **1966** 專線預約正式評估。")
        st.markdown("""
        **您可以這樣做：**
        1. 準備好家人的身分證與最近的病歷。
        2. 撥打 1966 告訴專員要申請「長照評估」。
        3. 如果家人還在住院，別忘了諮詢 <span class="orange-text">UIA好厝邊</span> 的「服務安排」！
        """, unsafe_allow_html=True)
        st.balloons()
    elif prob >= 0.4:
        st.warning("🟡 **目前在門檻邊緣：** 建議諮詢專業醫護，看看是否有其他專案。")
    else:
        st.info("⚪ **目前狀況還算健康：** 預防勝於治療！")

st.markdown("---")
st.caption("💌 UIA好厝邊關心您。本評估僅供參考，正式結果以政府照管專員評估為準。")
