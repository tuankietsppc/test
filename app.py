import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
import numpy as np  # type: ignore
import io
import os
from fpdf import FPDF # type: ignore
import plotly.io as pio  # type: ignore
import tempfile
from streamlit_chat import message  # type: ignore # Chat UI
from PIL import Image # type: ignore
import urllib.request
import base64
# Thiết lập tiêu đề và bố cục trang
# Đặt tiêu đề trang và chế độ bố cục rộng
st.set_page_config(page_title='Phân tích điểm thi', layout="wide")
st.title('📊 PHÂN TÍCH DỮ LIỆU ĐIỂM THI')  # Hiển thị tiêu đề lớn trên giao diện

# === ÁP DỤNG CSS TÙY CHỈNH CHO GIAO DIỆN ===
st.markdown("""
<style>
/* Tùy chỉnh nút chính */
div.stButton > button, .stDownloadButton button {
    background-color: #0072C6;  /* màu nền nút */
    color: white;               /* màu chữ */
    font-weight: bold;          /* chữ đậm */
    border-radius: 8px;         /* bo góc nút */
    padding: 10px 25px;         /* khoảng cách trong nút */
    border: none;               /* không viền */
    transition: 0.3s ease-in-out; /* hiệu ứng chuyển đổi */
    margin-top: 10px;           /* khoảng cách trên nút */
}
div.stButton > button:hover, .stDownloadButton button:hover {
    background-color: #005A9E;  /* đổi màu khi hover */
    transform: scale(1.03);     /* phóng to nhẹ */
}

/* Giao diện sidebar */
section[data-testid="stSidebar"] {
    background-color: #F0F5FA;  /* màu nền sidebar */
    border-right: 2px solid #C7D0E4; /* viền phải */
}
section[data-testid="stSidebar"] h2 {
    color: #0072C6;             /* màu chữ tiêu đề sidebar */
    font-size: 1.3rem;          /* cỡ chữ tiêu đề sidebar */
}

/* Tùy chỉnh hộp chọn */
div[data-baseweb="select"], div[data-baseweb="radio"], div[data-baseweb="checkbox"] {
    background-color: #ffffff;  /* nền trắng */
    border: 1px solid #0072C6; /* viền màu xanh */
    border-radius: 6px;         /* bo góc */
    padding: 10px;              /* khoảng cách trong hộp */
    margin-bottom: 12px;        /* khoảng cách dưới hộp */
}

/* Khung nội dung */
.khung_noi_dung {
    background-color: #ffffff;  /* nền trắng */
    border-radius: 12px;        /* bo góc */
    padding: 25px;              /* khoảng cách trong */
    margin-bottom: 30px;        /* khoảng cách dưới */
    box-shadow: 0px 2px 8px rgba(0, 114, 198, 0.1); /* đổ bóng */
}
.tieu_de_khung {
    font-size: 22px;            /* cỡ chữ tiêu đề khung */
    font-weight: 600;           /* chữ đậm vừa phải */
    color: #0072C6;             /* màu chữ */
    margin-bottom: 15px;        /* khoảng cách dưới */
}
</style>
""", unsafe_allow_html=True)  # Chèn CSS tùy chỉnh vào Streamlit
# Hiển thị uploader ở đây
# Tải file
uploaded_file = st.file_uploader("Chọn tệp Excel (.xlsx hoặc .xls)", type=["xlsx", "xls"])

# Dùng session_state để giữ trạng thái
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "du_lieu" not in st.session_state:
    st.session_state.du_lieu = None

# Hiển thị nút xác nhận sau khi chọn file
if uploaded_file:
    st.success("✅ Đã chọn file: " + uploaded_file.name)
    try:
        df = pd.read_excel(uploaded_file)

        # Đổi tên cột nếu có
        df = df.rename(columns={
            "TRUONG": "Trường THCS",
            "LOP": "Tên lớp",
            "GT": "GT",
            "DT": "Dân tộc"
        })

        st.session_state.du_lieu = df
        st.session_state.data_loaded = True
        st.success("✅ Dữ liệu đã được tải thành công.")

    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")


    # Kiểm tra các cột cần thiết tồn tại
    required_columns = ["Trường THCS", "Tên lớp"]
    if all(col in df.columns for col in required_columns):
        if st.session_state.data_loaded:
            du_lieu = st.session_state.du_lieu.copy()
        st.sidebar.markdown("### 🎯 Bộ lọc dữ liệu")
        st.sidebar.markdown("Lọc dữ liệu theo trường, lớp, giới tính, dân tộc và khoảng điểm để phân tích.")
        # --- Lọc theo Trường THCS ---
        truongs = du_lieu["Trường THCS"].dropna().unique().tolist()
        truongs.insert(0, "Tất cả")
        truong_chon = st.sidebar.multiselect("Chọn Trường THCS", truongs, default=["Tất cả"])

        # Nếu chọn "Tất cả", bỏ chọn các trường khác
        if "Tất cả" in truong_chon:
            truong_chon = [truong for truong in truong_chon if truong == "Tất cả"]

        # Cảnh báo nếu không chọn gì
        if not truong_chon:
            st.sidebar.warning("⚠️ Vui lòng chọn ít nhất một trường THCS.")
            st.stop()

        # Lọc dữ liệu nếu không chọn "Tất cả"
        if "Tất cả" not in truong_chon:
            du_lieu = du_lieu[du_lieu["Trường THCS"].isin(truong_chon)]



        # --- Lọc theo Tên lớp ---
        lop_list = du_lieu["Tên lớp"].dropna().unique().tolist()
        lop_list.insert(0, "Tất cả")
        lop_chon = st.sidebar.selectbox("Chọn Tên lớp", lop_list)
        if lop_chon != "Tất cả":
            du_lieu = du_lieu[du_lieu["Tên lớp"] == lop_chon]

        # --- Lọc theo Giới tính (GT) ---
        if "GT" in du_lieu.columns:
            gt_list = du_lieu["GT"].dropna().unique().tolist()
            gt_list.insert(0, "Tất cả")
            gt_chon = st.sidebar.selectbox("Chọn Giới tính", gt_list)
            if gt_chon != "Tất cả":
                du_lieu = du_lieu[du_lieu["GT"] == gt_chon]

        # --- Lọc theo Dân tộc ---
        if "Dân tộc" in du_lieu.columns:
            dt_list = du_lieu["Dân tộc"].dropna().unique().tolist()
            dt_list.insert(0, "Tất cả")
            dt_chon = st.sidebar.selectbox("Chọn Dân tộc", dt_list)
            if dt_chon != "Tất cả":
                du_lieu = du_lieu[du_lieu["Dân tộc"] == dt_chon]

        # Hiển thị dữ liệu đã lọc
        st.markdown('<div class="tieu_de_khung">📄 Dữ liệu sau khi lọc các trường thông tin:</div>', unsafe_allow_html=True)
        st.dataframe(du_lieu)
        
        # Hiển thị số dòng dữ liệu sau lọc
        so_dong = du_lieu.shape[0]
        st.write(f"✅ Số dòng dữ liệu sau khi lọc đơn vị: {so_dong}")

    else:
        st.warning("⚠️ File Excel cần có ít nhất 2 cột: 'TRUONG' và 'LOP'")

    if all(col in du_lieu.columns for col in ["Toán(lớp 9)", "Toán(KC)", "Ngữ văn(lớp 9)", "Ngữ văn(KC)"]):

        mon_chon = st.sidebar.selectbox("📘 Chọn môn cần phân tích", ["Toán", "Văn"])

        # Lấy tên cột tương ứng với môn chọn
        if mon_chon == "Toán":
            cot_lop9 = "Toán(lớp 9)"
            cot_kc = "Toán(KC)"
        else:
            cot_lop9 = "Ngữ văn(lớp 9)"
            cot_kc = "Ngữ văn(KC)"

        # Chuyển dữ liệu sang kiểu số, lỗi sẽ thành NaN
        du_lieu[cot_lop9] = pd.to_numeric(du_lieu[cot_lop9], errors='coerce')
        du_lieu[cot_kc] = pd.to_numeric(du_lieu[cot_kc], errors='coerce')

        avg_lop9 = du_lieu[cot_lop9].mean()
        avg_kc = du_lieu[cot_kc].mean()
        # --- Bộ lọc khoảng điểm (áp dụng cho cả cột lớp 9 và cột KC) ---
        ds_khoang_diem = ["Tất cả", "0 đến 2", "Trên 2 đến 5", "Trên 5 đến 8", "Trên 8 đến 10", "Vắng"]

        # multiselect với lựa chọn mặc định là tất cả
        khoang_diem_chon = st.sidebar.multiselect(
            "🎯 Chọn khoảng điểm (áp dụng cho lớp 9 và KC)",
            options=ds_khoang_diem,
            default=ds_khoang_diem  # Mặc định chọn tất cả
        )

        # Nếu chọn "Tất cả", tự động coi như chọn hết (trừ "Tất cả" chính nó)
        if "Tất cả" in khoang_diem_chon:
            khoang_diem_chon = [k for k in ds_khoang_diem if k != "Tất cả"]

        # Nếu không chọn gì, hiển thị cảnh báo và dừng
        if not khoang_diem_chon:
            st.sidebar.warning("⚠️ Bạn phải chọn ít nhất một khoảng điểm.")
            st.stop()


        # Hàm kiểm tra "vắng" (giả sử dữ liệu vắng thể hiện dưới dạng NaN hoặc chuỗi 'vắng', 'Vắng')
        def is_vang(x):
            if pd.isna(x):
                return True
            if isinstance(x, str) and x.strip().lower() == "vắng":
                return True
            return False

        # Nếu không chọn gì, không hiển thị dữ liệu
        if not khoang_diem_chon:
            du_lieu = du_lieu[[]]  # Trả về dataframe rỗng
        else:
            def thuoc_khoang(diem, danh_sach_khoang):
                if pd.isna(diem):
                    return "Vắng" in danh_sach_khoang
                if 0 <= diem <= 2:
                    return "0 đến 2" in danh_sach_khoang
                elif 2 < diem <= 5:
                    return "Trên 2 đến 5" in danh_sach_khoang
                elif 5 < diem <= 8:
                    return "Trên 5 đến 8" in danh_sach_khoang
                elif 8 < diem <= 10:
                    return "Trên 8 đến 10" in danh_sach_khoang
                return False

            du_lieu = du_lieu[
                du_lieu[cot_lop9].apply(lambda x: thuoc_khoang(x, khoang_diem_chon)) |
                du_lieu[cot_kc].apply(lambda x: thuoc_khoang(x, khoang_diem_chon))
            ]



        df_so_sanh = pd.DataFrame({
            "Loại": [f"{mon_chon} (lớp 9)", f"{mon_chon} (KC)"],
            "Điểm trung bình": [avg_lop9, avg_kc]
        })
        fig = px.bar(
            df_so_sanh,
            x="Loại",
            y="Điểm trung bình",
            title=f"📊 So sánh điểm trung bình môn {mon_chon} năm lớp 9 và {mon_chon} điểm thi",
            text="Điểm trung bình",
            color="Loại",
            color_discrete_sequence=["#1f77b4", "#ff7f0e"],
            template="plotly_white"
        )
        
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # Tạo cột phân loại khoảng điểm cho từng nguồn điểm
        def classify_range(diem):
            if pd.isna(diem):
                return "Vắng"
            elif 0 <= diem <= 2:
                return "0 đến 2"
            elif 2 < diem <= 5:
                return "Trên 2 đến 5"
            elif 5 < diem <= 8:
                return "Trên 5 đến 8"
            elif 8 < diem <= 10:
                return "Trên 8 đến 10"
            else:
                return "Khác"

        # Phân loại điểm theo khoảng
        du_lieu["Khoảng điểm lớp 9"] = du_lieu[cot_lop9].apply(classify_range)
        du_lieu["Khoảng điểm KC"] = du_lieu[cot_kc].apply(classify_range)

        # Lọc dữ liệu theo trường đã chọn (nếu có lọc trường)
        if "Trường THCS" in du_lieu.columns:
            if truong_chon and "Tất cả" not in truong_chon:
                du_lieu_filtered = du_lieu[du_lieu["Trường THCS"].isin(truong_chon)]
            else:
                du_lieu_filtered = du_lieu.copy()
        else:
            du_lieu_filtered = du_lieu.copy()

        # Lọc theo khoảng điểm đã chọn
        def is_in_selected_range(x):
            return x in khoang_diem_chon

        du_lieu_filtered = du_lieu_filtered[
            du_lieu_filtered["Khoảng điểm lớp 9"].apply(is_in_selected_range) |
            du_lieu_filtered["Khoảng điểm KC"].apply(is_in_selected_range)
        ]
        # Hiển thị dữ liệu sau khi lọc theo khoảng điểm
        st.markdown('<div class="tieu_de_khung">📄 Dữ liệu sau khi lọc theo khoảng điểm:</div>', unsafe_allow_html=True)
        st.dataframe(du_lieu_filtered)

        # Hiển thị số dòng dữ liệu
        st.write(f"📌 Số dòng dữ liệu sau khi lọc khoảng điểm: {du_lieu_filtered.shape[0]}")

        # Tạo bảng tần suất dựa trên dữ liệu đã lọc và chỉ lấy khoảng điểm được chọn
        if khoang_diem_chon:
            pie_lop9 = du_lieu_filtered["Khoảng điểm lớp 9"].value_counts().reindex(
                khoang_diem_chon, fill_value=0
            ).reset_index()
            pie_lop9.columns = ["Khoảng điểm", "Số lượng"]

            pie_kc = du_lieu_filtered["Khoảng điểm KC"].value_counts().reindex(
                khoang_diem_chon, fill_value=0
            ).reset_index()
            pie_kc.columns = ["Khoảng điểm", "Số lượng"]

            # Tạo 2 cột để hiển thị biểu đồ cạnh nhau
            col1, col2 = st.columns(2)

            with col1:
                fig_pie1 = px.pie(
                    pie_lop9,
                    names="Khoảng điểm",
                    values="Số lượng",
                    title=f"🎯 Phân bố điểm {mon_chon} lớp 9",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie1.update_traces(textinfo='percent+label')
                st.plotly_chart(fig_pie1, use_container_width=True, key="pie_lop9")

            with col2:
                fig_pie2 = px.pie(
                    pie_kc,
                    names="Khoảng điểm",
                    values="Số lượng",
                    title=f"🎯 Phân bố điểm {mon_chon} KC",
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                fig_pie2.update_traces(textinfo='percent+label')
                st.plotly_chart(fig_pie2, use_container_width=True, key="pie_chart_kc")

            # ==== BẢNG THỐNG KÊ SỐ LƯỢNG THEO KHOẢNG ĐIỂM ====
            with st.container():
                st.markdown('<div class="khung_noi_dung">', unsafe_allow_html=True)
                st.markdown('<div class="tieu_de_khung">📋 Bảng thống kê số lượng học sinh theo khoảng điểm</div>', unsafe_allow_html=True)

                # Gộp dữ liệu từ hai bảng tần suất thành một bảng
                bang_thong_ke = pd.DataFrame({
                    "Khoảng điểm": pie_lop9["Khoảng điểm"],
                    f"{mon_chon} lớp 9": pie_lop9["Số lượng"],
                    f"{mon_chon} KC": pie_kc["Số lượng"]
                })

                # Căn giữa văn bản trong bảng
                styled_bang = bang_thong_ke.style.set_properties(**{
                    'text-align': 'center'
                })

                st.dataframe(styled_bang, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Vui lòng chọn ít nhất một khoảng điểm để hiển thị biểu đồ và bảng thống kê.")

    # ==== BIỂU ĐỒ ĐƯỜNG SO SÁNH KHOẢNG ĐIỂM GIỮA CÁC TRƯỜNG ====
    st.markdown('<div class="khung_noi_dung">', unsafe_allow_html=True)
    st.markdown('<div class="tieu_de_khung">📈 So sánh phân bố điểm theo trường (biểu đồ đường)</div>', unsafe_allow_html=True)

    # Lọc các khoảng điểm cần thiết (không bao gồm NaN/Khác)
    khoang_diem_order = ["0 đến 2", "Trên 2 đến 5", "Trên 5 đến 8", "Trên 8 đến 10", "Vắng"]

    # Gom nhóm và đếm số lượng theo từng khoảng điểm và trường
    df_line = du_lieu[du_lieu["Khoảng điểm KC"].isin(khoang_diem_chon)] \
    .groupby(["Trường THCS", "Khoảng điểm KC"]).size().reset_index(name="Số lượng")
    df_line["Khoảng điểm KC"] = pd.Categorical(df_line["Khoảng điểm KC"], categories=khoang_diem_order, ordered=True)

    # Sắp xếp khoảng điểm theo thứ tự logic
    df_line["Khoảng điểm KC"] = pd.Categorical(df_line["Khoảng điểm KC"], categories=khoang_diem_order, ordered=True)

    # Tạo biểu đồ đường
    fig_line = px.line(
        df_line,
        x="Khoảng điểm KC",
        y="Số lượng",
        color="Trường THCS",
        markers=True,
        title="📉 So sánh phân bố điểm KC giữa các trường",
        line_shape="spline",
        template="plotly_white"
    )
    fig_line.update_traces(mode="lines+markers")
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
    # === BIỂU ĐỒ CỘT PHÂN BỐ KHOẢNG ĐIỂM THEO TRƯỜNG ===
    st.markdown('<div class="khung_noi_dung">', unsafe_allow_html=True)
    st.markdown('<div class="tieu_de_khung">🏫 Phân bố học sinh theo khoảng điểm KC của từng trường</div>', unsafe_allow_html=True)

    # Tính toán số lượng học sinh theo khoảng điểm KC và trường
    df_bar = du_lieu[du_lieu["Khoảng điểm KC"].isin(khoang_diem_chon)] \
    .groupby(["Khoảng điểm KC", "Trường THCS"]).size().reset_index(name="Số lượng")
    df_bar["Khoảng điểm KC"] = pd.Categorical(df_bar["Khoảng điểm KC"], categories=khoang_diem_order, ordered=True)

    df_bar["Khoảng điểm KC"] = pd.Categorical(df_bar["Khoảng điểm KC"], categories=khoang_diem_order, ordered=True)

    # Vẽ biểu đồ cột nhóm
    fig_bar = px.bar(
        df_bar,
        x="Khoảng điểm KC",
        y="Số lượng",
        color="Trường THCS",
        barmode="group",
        title="📊 Phân bố học sinh theo khoảng điểm KC của từng trường",
        template="plotly_white"
    )
    # Lưu biểu đồ vào file tạm (dành cho PDF)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_bar:
        fig_bar.write_image(tmp_bar.name, width=700, height=400)
        path_bar_chart = tmp_bar.name  # Lưu lại đường dẫn để chèn vào PDF

        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Hàm tải font Unicode nếu chưa có
    
    def ensure_unicode_font():
        base_url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/"
        fonts = [
            "DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
        ]
        for filename in fonts:
            if not os.path.exists(filename):
                print(f"Downloading {filename}...")
                urllib.request.urlretrieve(base_url + filename, filename)
            else:
                print(f"{filename} already exists, skipping download.")

    ensure_unicode_font()



    class PDF(FPDF):
        def __init__(self):
            super().__init__()
            self.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
            self.add_font("DejaVu", "B", "DejaVuSans-Bold.ttf", uni=True)
            self.set_font("DejaVu", "", 12)

        def footer(self):
            self.set_y(-15)
            self.set_font("DejaVu", "B", 10)
            self.set_text_color(128)
            self.cell(0, 10, f"Trang {self.page_no()}", align="C")

    # ...

    if st.button("📥 Tạo báo cáo PDF"):
        ensure_unicode_font()
        pdf = PDF()
        pdf.add_page()

        pdf.set_font("DejaVu", "B", 18)
        pdf.cell(0, 15, f"BÁO CÁO PHÂN TÍCH MÔN {mon_chon.upper()}", ln=True, align="C")
        pdf.set_font("DejaVu", "", 12)
        pdf.ln(10)

        page_width = 210
        table_width = 70 + 50  # tổng chiều rộng bảng

        # tính x để căn giữa
        x = (page_width - table_width) / 2

        pdf.set_x(x)  # đặt vị trí x cho tiêu đề bảng
        pdf.set_font("DejaVu", "B", 12)
        pdf.set_fill_color(230, 230, 230)

        pdf.cell(70, 10, "Loại điểm", border=1, align="C", fill=True)
        pdf.cell(50, 10, "Điểm trung bình", border=1, align="C", fill=True)
        pdf.ln()

        pdf.set_x(x)  # đặt lại x cho dòng tiếp theo
        pdf.set_font("DejaVu", "", 12)
        pdf.cell(70, 10, "Điểm trung bình lớp 9", border=1, align="L")
        pdf.cell(50, 10, f"{avg_lop9:.2f}", border=1, align="C")
        pdf.ln()

        pdf.set_x(x)
        pdf.cell(70, 10, "Điểm trung bình KC", border=1, align="L")
        pdf.cell(50, 10, f"{avg_kc:.2f}", border=1, align="C")
        pdf.ln(15)

        fig.update_layout(
            margin=dict(t=80, b=40, l=40, r=40)  # đủ không gian cho chữ, tiêu đề
        )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.write_image(tmpfile.name, width=900, height=500, scale=3)  # scale cao để ảnh sắc nét
            pdf.image(tmpfile.name, x=10, y=None, w=190)  # co về đúng kích thước hiển thị

        pdf.ln(15)


        # Cập nhật margin và xuất biểu đồ tròn sắc nét
        fig_pie1.update_layout(margin=dict(t=60, b=40, l=40, r=40))
        fig_pie2.update_layout(margin=dict(t=60, b=40, l=40, r=40))

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp1, \
            tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp2:

            fig_pie1.write_image(tmp1.name, width=500, height=500, scale=2)
            fig_pie2.write_image(tmp2.name, width=500, height=500, scale=2)

            y_start = pdf.get_y()
            pdf.image(tmp1.name, x=15, y=y_start, w=85)
            pdf.image(tmp2.name, x=110, y=y_start, w=85)

        pdf.ln(100)

        # Thiết lập font và tiêu đề
        pdf.set_font("DejaVu", "B", 13)
        pdf.cell(0, 12, "📊 Phân bố học sinh theo khoảng điểm KC", ln=True, align="C")
        pdf.ln(5)

        # Tạo biểu đồ sắc nét hơn
        if 'fig_bar' in locals():  # nếu bạn vẫn còn figure trong bộ nhớ
            path_bar_chart = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
            fig_bar.update_layout(margin=dict(t=80, b=60, l=60, r=40))
            fig_bar.write_image(path_bar_chart, width=1000, height=500, scale=3)

        # Chèn vào PDF
        if 'path_bar_chart' in locals():
            pdf.image(path_bar_chart, x=10, w=190)
            pdf.ln(10)




        # Bảng
        pdf.set_font("DejaVu", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 14, "Bảng thống kê số lượng học sinh theo khoảng điểm:", ln=True, align="C")
        pdf.ln(6)

        col_widths = [65, 60, 60]
        headers = ["Khoảng điểm", f"{mon_chon} lớp 9", f"{mon_chon} KC"]

        # Header bảng với nền màu xanh nhạt và chữ đậm trắng
        pdf.set_fill_color(70, 130, 180)  # xanh dương đậm
        pdf.set_text_color(255, 255, 255)  # trắng
        pdf.set_font("DejaVu", "B", 12)
        for i in range(len(headers)):
            pdf.cell(col_widths[i], 14, headers[i], border=1, align='C', fill=True)
        pdf.ln()

        # Nội dung bảng với màu xen kẽ
        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(0, 0, 0)
        for i in range(len(bang_thong_ke)):
            row = bang_thong_ke.iloc[i]
            fill = i % 2 == 0
            if fill:
                pdf.set_fill_color(235, 245, 255)  # xanh rất nhạt
            else:
                pdf.set_fill_color(255, 255, 255)  # trắng
            
            pdf.cell(col_widths[0], 14, str(row['Khoảng điểm']), border=1, align='C', fill=fill)
            pdf.cell(col_widths[1], 14, str(row[f"{mon_chon} lớp 9"]), border=1, align='C', fill=fill)
            pdf.cell(col_widths[2], 14, str(row[f"{mon_chon} KC"]), border=1, align='C', fill=fill)
            pdf.ln()


        # Xuất PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf.output(tmp_pdf.name)
            with open(tmp_pdf.name, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                # HTML cho nút tải PDF
                href = f"""
                <div >
                    <a href="data:application/pdf;base64,{b64}" download="bao_cao_phan_tich.pdf"
                        style="
                            display: inline-block;
                            padding: 12px 24px;
                            font-size: 16px;
                            font-weight: 600;
                            color: white;
                            background: linear-gradient(90deg, #007bff 0%, #0056b3 100%);
                            border: none;
                            border-radius: 8px;
                            text-decoration: none;
                            box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                            transition: all 0.3s ease;
                        "
                        onmouseover="this.style.background='linear-gradient(90deg, #0056b3 0%, #003f7f 100%)'"
                        onmouseout="this.style.background='linear-gradient(90deg, #007bff 0%, #0056b3 100%)'"
                    >
                        📄 Tải về báo cáo PDF
                    </a>
                </div>
                """
                st.markdown(href, unsafe_allow_html=True)

    # ==== 1. Danh sách từ khóa và câu trả lời mẫu ====
    RESPONSE_TEMPLATES = [
        {
            "keywords": ["tải báo cáo", "pdf", "xuất pdf"],
            "response": "📄 Để tải báo cáo phân tích dưới dạng PDF:\n1. Cuộn xuống cuối trang.\n2. Nhấn **📥 Tải báo cáo PDF**.\nHệ thống sẽ tạo file gồm biểu đồ, thống kê và bảng dữ liệu chi tiết theo lựa chọn của bạn."
        },
        {
            "keywords": ["điểm trung bình", "trung bình lớp 9", "trung bình kc"],
            "response": "📊 Điểm trung bình của môn học được tính tự động sau khi bạn chọn môn. Hệ thống sẽ hiển thị biểu đồ cột để bạn so sánh giữa điểm lớp 9 và điểm thi KC."
        },
        {
            "keywords": ["khoảng điểm", "phân tích khoảng điểm", "thống kê điểm"],
            "response": "🎯 Phân tích khoảng điểm giúp bạn biết số lượng học sinh thuộc các nhóm điểm cụ thể. Hệ thống hiển thị biểu đồ tròn và bảng thống kê tương ứng."
        },
        {
            "keywords": ["lọc", "bộ lọc", "lọc dữ liệu"],
            "response": "🔍 Bạn có thể sử dụng bộ lọc ở **thanh bên trái** để phân tích theo:\n- Trường\n- Lớp\n- Giới tính\n- Dân tộc\n- Khoảng điểm"
        },
        {
            "keywords": ["giới tính", "nam nữ"],
            "response": "⚧️ Bạn có thể lọc theo **giới tính** để so sánh điểm số giữa nam và nữ học sinh."
        },
        {
            "keywords": ["dân tộc"],
            "response": "🧬 Bộ lọc **dân tộc** giúp phân tích riêng nhóm học sinh dân tộc thiểu số nếu có."
        },
        {
            "keywords": ["bắt đầu", "hướng dẫn sử dụng", "sử dụng hệ thống"],
            "response": "🚀 Hướng dẫn nhanh:\n1. Tải file Excel có điểm thi.\n2. Chọn bộ lọc bên trái.\n3. Chọn môn cần phân tích.\n4. Xem biểu đồ, bảng thống kê.\n5. Nhấn nút **Tải báo cáo PDF** nếu muốn xuất kết quả."
        },
        {
            "keywords": ["file", "nhập dữ liệu", "excel", "định dạng file"],
            "response": "📁 Bạn cần tải lên file `.xlsx` hoặc `.xls` có các cột: `TRUONG`, `LOP`, `GT`, `DT`, `Toán(lớp 9)`, `Toán(KC)` hoặc tương đương."
        },
        {
            "keywords": ["môn học", "toán", "ngữ văn"],
            "response": "📚 Hệ thống hỗ trợ phân tích môn **Toán** và **Ngữ văn**. Bạn có thể chọn môn từ thanh bên trái."
        },
        {
            "keywords": ["lỗi", "bị lỗi", "không chạy", "không phân tích"],
            "response": "⚠️ Nếu gặp lỗi:\n- Kiểm tra lại file có đúng định dạng không.\n- Đảm bảo tên các cột đúng như yêu cầu.\n- Nếu vẫn lỗi, bạn có thể thử file khác hoặc liên hệ hỗ trợ."
        }
    ]

    # ==== 2. Hàm phản hồi chatbot ====
    def guide_bot_reply(user_input: str) -> str:
        user_input = user_input.lower()
        for template in RESPONSE_TEMPLATES:
            if any(keyword in user_input for keyword in template["keywords"]):
                return template["response"]
        return (
            "🤖 Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. Bạn có thể hỏi:\n"
            "- Làm sao để tải báo cáo?\n"
            "- Phân tích điểm trung bình thế nào?\n"
            "- Cách lọc dữ liệu theo lớp hoặc trường?\n"
            "Hoặc nhấn vào nút gợi ý bên dưới nhé!"
        )

    # ==== 3. Hiển thị ChatBot Hướng dẫn ====
    st.subheader("💬 Hướng dẫn sử dụng hệ thống")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Xin chào! Tôi là trợ lý phân tích điểm thi. Bạn có thể hỏi tôi về cách nhập dữ liệu, phân tích điểm, xuất PDF hoặc cách dùng bộ lọc nhé!"
            }
        ]

    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=(msg["role"] == "user"), key=f"msg_{i}")

    # ==== 4. Ô nhập từ người dùng ====
    if prompt := st.chat_input("Nhập câu hỏi hoặc từ khóa cần hỗ trợ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        reply = guide_bot_reply(prompt)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # ==== 5. Gợi ý câu hỏi nhanh ====
    st.markdown("### 💡 Gợi ý một số câu hỏi:")
    cols = st.columns(2)
    questions = [
        "📄 Làm sao để xuất báo cáo PDF?",
        "📊 Phân tích điểm trung bình",
        "🔍 Cách lọc dữ liệu theo lớp",
        "🎯 Phân tích khoảng điểm",
        "🗂 File cần định dạng thế nào?",
        "⚠️ Gặp lỗi khi phân tích"
    ]
    for i, q in enumerate(questions):
        with cols[i % 2]:
            if st.button(q):
                st.session_state.messages.append({"role": "user", "content": q})
                st.session_state.messages.append({"role": "assistant", "content": guide_bot_reply(q)})
                st.rerun()
