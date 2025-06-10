import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io

st.set_page_config(page_title='Phân tích điểm thi', layout="wide")
st.title('📊 PHÂN TÍCH DỮ LIỆU ĐIỂM THI')

# === CSS CHUYÊN NGHIỆP ===
st.markdown("""
<style>
/* Nút và màu chính */
div.stButton > button, .stDownloadButton button {
    background-color: #0072C6;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 25px;
    border: none;
    transition: 0.3s ease-in-out;
    margin-top: 10px;
}
div.stButton > button:hover, .stDownloadButton button:hover {
    background-color: #005A9E;
    transform: scale(1.03);
}
/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #F0F5FA;
    border-right: 2px solid #C7D0E4;
}
section[data-testid="stSidebar"] h2 {
    color: #0072C6;
    font-size: 1.3rem;
}
/* Bộ lọc */
div[data-baseweb="select"], div[data-baseweb="radio"], div[data-baseweb="checkbox"] {
    background-color: #ffffff;
    border: 1px solid #0072C6;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 12px;
}
/* Khung nội dung */
.box {
    background-color: #ffffff;
    /* border: 1px solid #0072C6; */  /* Bỏ viền */
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 30px;
    box-shadow: 0px 2px 8px rgba(0, 114, 198, 0.1);
}
.box-title {
    font-size: 22px;
    font-weight: 600;
    color: #0072C6;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)


# === TẢI FILE ===
uploaded_file = st.file_uploader('📤 Chọn file Excel', type='xlsx')

if uploaded_file:
    df = pd.read_excel(uploaded_file, engine='openpyxl')
    df_raw = df.copy()

    # === SIDEBAR LỌC ===
    st.sidebar.header("🎯 Bộ lọc dữ liệu")

    hoidong = st.sidebar.multiselect("Chọn hội đồng thi:", df["TENHD"].unique(), default=df["TENHD"].unique())
    diem_van = st.sidebar.radio("Lọc điểm Ngữ văn:", ["Tất cả", "Từ 0 đến dưới 5", "Từ 5 trở lên", "Vắng"])
    diem_toan = st.sidebar.radio("Lọc điểm Toán:", ["Tất cả", "Từ 0 đến dưới 5", "Từ 5 trở lên", "Vắng"])
    diem_anh = st.sidebar.radio("Lọc điểm Tiếng Anh:", ["Tất cả", "Từ 0 đến dưới 5", "Từ 5 trở lên", "Vắng"])
    diem_xt = st.sidebar.radio("Lọc điểm xét tuyển:", ["Tất cả", "Từ 0 đến dưới 10", "Từ 10 đến 20", "Từ 20 đến 30"])
    loc_liet = st.sidebar.checkbox("Chỉ hiển thị thí sinh bị liệt")

    # === HÀM LỌC ===
    def loc_diem(df, cot, lua_chon):
        df[cot] = df[cot].astype(str).str.strip()
        if lua_chon == "Từ 0 đến dưới 5":
            return df[pd.to_numeric(df[cot], errors='coerce') < 5]
        elif lua_chon == "Từ 5 trở lên":
            return df[pd.to_numeric(df[cot], errors='coerce') >= 5]
        elif lua_chon == "Vắng":
            return df[df[cot].str.lower() == "vắng"]
        return df

    def loc_diem_xet_tuyen(df, lua_chon):
        cot = "DIEMXETTUYEN"
        df[cot] = pd.to_numeric(df[cot], errors='coerce')
        if lua_chon == "Từ 0 đến dưới 10":
            return df[(df[cot] >= 0) & (df[cot] < 10)]
        elif lua_chon == "Từ 10 đến 20":
            return df[(df[cot] >= 10) & (df[cot] <= 20)]
        elif lua_chon == "Từ 20 đến 30":
            return df[(df[cot] > 20) & (df[cot] <= 30)]
        return df

    # === ÁP DỤNG LỌC ===
    df = df[df["TENHD"].isin(hoidong)]
    df = loc_diem(df, "DTNGUVANIN", diem_van)
    df = loc_diem(df, "DTTOANIN", diem_toan)
    df = loc_diem(df, "DTTIENGANHIN", diem_anh)
    df = loc_diem_xet_tuyen(df, diem_xt)
    if loc_liet and "LIET" in df.columns:
        df = df[df["LIET"].astype(str).str.strip() == "Liệt"]

    # === THỐNG KÊ VÀ BIỂU ĐỒ ===
    count_raw = df_raw["TENHD"].value_counts().reset_index()
    count_raw.columns = ["TENHD", "Tổng số thí sinh"]
    count_filtered = df["TENHD"].value_counts().reset_index()
    count_filtered.columns = ["TENHD", "Số thí sinh sau lọc"]
    summary_df = pd.merge(count_raw, count_filtered, on="TENHD", how="outer").fillna(0)
    summary_df = summary_df.astype({"Tổng số thí sinh": int, "Số thí sinh sau lọc": int})

    # === BIỂU ĐỒ CỘT ===
    st.markdown('<div class="box"><div class="box-title">📊 So sánh số lượng thí sinh theo hội đồng</div>', unsafe_allow_html=True)
    fig_compare = px.bar(
        summary_df.melt(id_vars="TENHD", value_vars=["Tổng số thí sinh", "Số thí sinh sau lọc"],
                        var_name="Loại", value_name="Số lượng"),
        x="TENHD", y="Số lượng", color="Loại", barmode="group"
    )
    st.plotly_chart(fig_compare)
    st.markdown('</div>', unsafe_allow_html=True)

    # === BIỂU ĐỒ TRÒN ===
    st.markdown('<div class="box"><div class="box-title">🥧 Tỷ lệ tổng số thí sinh theo hội đồng</div>', unsafe_allow_html=True)
    fig_pie = px.pie(summary_df, names="TENHD", values="Tổng số thí sinh", hole=0.3)
    st.plotly_chart(fig_pie)
    st.markdown('</div>', unsafe_allow_html=True)

    # === BIỂU ĐỒ SIN ===
    st.markdown('<div class="box"><div class="box-title">🌊 Biểu đồ sin theo tỷ lệ thí sinh</div>', unsafe_allow_html=True)
    max_val = summary_df["Tổng số thí sinh"].max()
    x = np.linspace(0, 2 * np.pi, len(summary_df))
    y = np.sin(x) * (summary_df["Tổng số thí sinh"] / max_val)
    fig_sin = px.line(x=summary_df["TENHD"], y=y, labels={"x": "Hội đồng thi", "y": "Giá trị sin"})
    st.plotly_chart(fig_sin)
    st.markdown('</div>', unsafe_allow_html=True)

    # === DỮ LIỆU ĐÃ LỌC ===
    st.dataframe(df)
    st.markdown(f"""
        <p style='font-size:17px; font-weight:bold; color:#0072C6;'>Số lượng thí sinh hiển thị: {len(df)}</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # === TẢI XUỐNG ===
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='DuLieuDaLoc', index=False)
    st.download_button(
        label="📥 Tải xuống dữ liệu đã lọc",
        data=buffer.getvalue(),
        file_name="diem_thi_da_loc.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown('</div>', unsafe_allow_html=True)
