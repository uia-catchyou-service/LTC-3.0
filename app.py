import streamlit as st
import numpy as np

# 1. 網頁配置
st.set_page_config(
    page_title="UIA好厝邊-長照補助小幫手", 
    page_icon="🏡",
    layout="centered" 
)

# --- CSS 樣式 ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    html, body, [class*="css"] { font-family: "Microsoft JhengHei", sans-serif; }
    h1 { color: #F39800 !important; font-size: 1.8rem !important; text-align: center; }
    .main-intro { text-align: center; color: #555; line-height: 1.6; margin-bottom: 1.5rem; }
    .stCheckbox, .stRadio, .stSlider, .stSelectbox {
        background-color: #FDF7EF; padding: 15px; border-radius: 12px; margin-bottom: 5px; border: 1px solid #FFE4B5;
    }
    .stButton>button {
        background-color: #F39800; color: white; border-radius: 15px; padding: 0.8rem 1rem;
        font-size: 1.2rem; font-weight: bold; width: 100%; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .result-box { text-align: center; padding: 20px; background-color: #FFF; border: 2px solid #F39800; border-radius: 20px; margin: 20px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>長照補助資格測評器</h1>", unsafe_allow_html=True)
st.markdown('<div class="main-intro">照顧路上，您辛苦了！<br>跟著好厝邊簡單評估長照 3.0 資格。</div>', unsafe_allow_html=True)

# 3. 第一步：基本身分
st.subheader("1. 瞭解基本狀況")
age = st.slider("親屬年齡", 0, 125, 65)
is_rich = False 

col_check1, col_check2 = st.columns(2)
with col_check1:
    is_aboriginal = st.checkbox("具有原住民身分")
    has_disability_card = st.checkbox("領有身心障礙證明")
with col_check2:
    is_pac = st.checkbox("急性後期照護計畫(PAC)")
    dementia = st.checkbox("有失智症狀 (確診或疑似)")

with st.expander("💰 點此評估補助比例 (選填)"):
    is_rich = st.checkbox("去年所得稅率達 20% 以上或股利所得採分開計稅者")

# 4. 第二步：18 題失能狀況詳細評估 (分頁設計)
st.subheader("2. 日常生活活動評估 (ADL & IADL)")
tab1, tab2, tab3 = st.tabs(["📍 身體照顧", "📍 居家生活", "📍 健康與管理"])

with tab1:
    st.write("請勾選身體基礎功能狀況：")
    a1 = st.radio("進食：", ["可自行取食", "需人幫忙", "完全無法"], horizontal=True)
    a2 = st.radio("洗澡：", ["可獨立完成", "需人協助"], horizontal=True)
    a3 = st.radio("個人衛生：", ["可自行刷牙洗臉", "需人協助"], horizontal=True)
    a4 = st.radio("穿脫衣服：", ["可自行穿好", "需人幫忙一半", "完全無法"], horizontal=True)
    a5 = st.radio("排便/尿控制：", ["可自行控制", "偶爾失禁", "完全失禁"], horizontal=True)
    a6 = st.radio("如廁：", ["可獨立完成", "需人扶持", "需完全幫忙"], horizontal=True)

with tab2:
    st.write("請勾選居家獨立生活狀況：")
    b1 = st.radio("移位/走動：", ["健步如飛", "需要扶持", "需輪椅", "臥床"], horizontal=True)
    b2 = st.radio("上下樓梯：", ["可自行上下", "需人稍微指導", "無法上下"], horizontal=True)
    b3 = st.radio("上街購物：", ["獨力完成", "需人陪同", "完全無法"], horizontal=True)
    b4 = st.radio("外出活動：", ["能搭公車/捷運", "需人陪伴", "完全不能"], horizontal=True)
    b5 = st.radio("食物烹調：", ["獨力完成", "可幫忙加熱", "需人煮好"], horizontal=True)
    b6 = st.radio("家務維持：", ["獨力完成", "需人幫忙"], horizontal=True)

with tab3:
    st.write("請勾選管理與通訊狀況：")
    c1 = st.radio("洗衣服：", ["獨力完成", "僅能洗小件", "完全無法"], horizontal=True)
    c2 = st.radio("服用藥物：", ["自己負責", "需人提醒", "完全無法"], horizontal=True)
    c3 = st.radio("電話使用：", ["獨力撥號應答", "僅能接聽", "完全無法"], horizontal=True)
    c4 = st.radio("財務管理：", ["獨力理財", "僅能處理小錢", "完全無法"], horizontal=True)

# 5. 邏輯運算 (結合 18 題失能訊號)
def calculate_3_0_logic():
    # 計算「需要協助」的總題數
    all_ans = [a1, a2, a3, a4, a5, a6, b1, b2, b3, b4, b5, b6, c1, c2, c3, c4]
    help_needed = sum(1 for x in all_ans if "需" in x or "無法" in x or "不能" in x or "失禁" in x)
    
    # 基礎權重
    z = -5.0
    if dementia or has_disability_card: z += 4.0 # 失智與身障收案權重高
    if is_pac: z += 3.5 # PAC 銜接權重
    if (age >= 65) or (is_aboriginal and age >= 55): z += 1.5
    
    # 根據 18 題的失能訊號加權
    z += help_needed * 0.8
    
    prob = 1 / (1 + np.exp(-z))
    return prob

# 6. 結果呈現
if st.button("✨ 點我得知符合機率"):
    prob = calculate_3_0_logic()
    res_color = "#E67E22" if is_rich else "#F39800"
    
    # 推估 CMS 等級
    cms_label = "2 級以上 (符合補助)" if prob >= 0.5 else "1 級 (目前尚健康)"
    
    st.markdown(f"""
    <div class="result-box" style="border-color: {res_color};">
        <h2 style='color:{res_color}; margin:0;'>推估 CMS 等級：{cms_label}</h2>
        <div style='font-size: 3.5rem; font-weight: bold; color:{res_color};'>{prob*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

    if prob >= 0.5:
        st.markdown("### 💡 補助權益小筆記")
        col1, col2 = st.columns(2)
        with col1:
            if is_rich: st.info("**🏠 居家/社區照顧**\n\n自付額約為 **16%**。")
            else: st.success("**🏠 居家/社區照顧**\n\n您可能符合**中低收入**，自付額僅 **0%~5%**！")
        with col2:
            if is_rich: st.error("**🏨 住宿機構補助**\n\n因稅率達 20%，**不符合** 12 萬補助。")
            else: st.success("**🏨 住宿機構補助**\n\n符合所得
