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

# === TẢI FILE EXCEL ===
tep_tai_len = st.file_uploader(
    '📤 Chọn file Excel hoặc CSV',
    type=['xlsx', 'csv'])  # Cho phép tải lên cả hai định dạng


if tep_tai_len:
    if tep_tai_len.name.endswith('.xlsx'):
        du_lieu = pd.read_excel(tep_tai_len, engine='openpyxl')
    elif tep_tai_len.name.endswith('.csv'):
        du_lieu = pd.read_csv(tep_tai_len, encoding='utf-8')  # Hoặc encoding='utf-8-sig' nếu lỗi font
    else:
        st.error("Định dạng file không hợp lệ. Chỉ hỗ trợ .xlsx và .csv.")
        st.stop()
    du_lieu_goc = du_lieu.copy()  # Sao lưu dữ liệu gốc để sử dụng sau này

    # === LỌC DỮ LIỆU TRONG THANH BÊN ===
    st.sidebar.header("🎯 Bộ lọc dữ liệu")  # Tiêu đề bộ lọc ở sidebar

    # Kiểm tra đủ cột cần thiết
    if all(cot in du_lieu.columns for cot in ["DONVI", "TRUONG", "LOP"]):
        # Lọc Đơn vị
        ds_don_vi = du_lieu_goc["DONVI"].dropna().unique().tolist()
        ds_don_vi.insert(0, "Tất cả")
        don_vi_chon = st.sidebar.selectbox("Chọn đơn vị", ds_don_vi)

        du_lieu_don_vi = du_lieu_goc.copy()
        if don_vi_chon != "Tất cả":
            du_lieu_don_vi = du_lieu_don_vi[du_lieu_don_vi["DONVI"]
                                            == don_vi_chon]

        # Lọc Trường (sau khi lọc đơn vị)
        ds_truong = du_lieu_don_vi["TRUONG"].dropna().unique().tolist()
        ds_truong.insert(0, "Tất cả")
        truong_chon = st.sidebar.selectbox("Chọn trường", ds_truong)

        du_lieu_truong = du_lieu_don_vi.copy()
        if truong_chon != "Tất cả":
            du_lieu_truong = du_lieu_truong[du_lieu_truong["TRUONG"]
                                            == truong_chon]

        # Lọc Lớp (sau khi lọc trường)
        ds_lop = du_lieu_truong["LOP"].dropna().unique().tolist()
        ds_lop.insert(0, "Tất cả")
        lop_chon = st.sidebar.selectbox("Chọn lớp", ds_lop)

        du_lieu = du_lieu_truong.copy()
        if lop_chon != "Tất cả":
            du_lieu = du_lieu[du_lieu["LOP"] == lop_chon]

        # Lọc Giới tính (nếu có cột)
        if "GT" in du_lieu.columns:
            ds_gioi_tinh = du_lieu["GT"].dropna().unique().tolist()
            ds_gioi_tinh.insert(0, "Tất cả")
            gioi_tinh_chon = st.sidebar.selectbox(
                "Chọn giới tính", ds_gioi_tinh)

            if gioi_tinh_chon != "Tất cả":
                du_lieu = du_lieu[du_lieu["GT"] == gioi_tinh_chon]
        else:
            gioi_tinh_chon = "Không có cột GT"

        # Lọc Dân tộc (nếu có cột)
        if "DT" in du_lieu.columns:
            ds_dan_toc = du_lieu["DT"].dropna().unique().tolist()
            ds_dan_toc.insert(0, "Tất cả")
            dan_toc_chon = st.sidebar.selectbox("Chọn dân tộc", ds_dan_toc)

            if dan_toc_chon != "Tất cả":
                du_lieu = du_lieu[du_lieu["DT"] == dan_toc_chon]
        else:
            dan_toc_chon = "Không có cột DT"

        # Hiển thị lựa chọn đã chọn
        st.write("Bạn đã chọn:")
        st.markdown(f"- **Đơn vị:** {don_vi_chon}")
        st.markdown(f"- **Trường:** {truong_chon}")
        st.markdown(f"- **Lớp:** {lop_chon}")
        st.markdown(f"- **Giới tính:** {gioi_tinh_chon}")
        st.markdown(f"- **Dân tộc:** {dan_toc_chon}")
    else:
        # Cảnh báo nếu thiếu cột
        st.warning(
            "Không tìm thấy đủ các cột 'DONVI', 'TRUONG', 'LOP' trong file Excel.")

    # === HIỂN THỊ DỮ LIỆU SAU LỌC ===
    st.dataframe(du_lieu)  # Hiển thị bảng dữ liệu đã lọc
    so_dong_du_lieu = du_lieu.shape[0]  # Lấy số dòng dữ liệu
    st.write(f"Số dòng của bảng là: {so_dong_du_lieu}")  # Hiển thị số dòng

    # === PHÂN TÍCH KHOẢNG ĐIỂM CÁC MÔN ===
    st.sidebar.markdown("---")  # Dòng kẻ ngăn cách trong sidebar
    # Tiêu đề phụ trong sidebar
    st.sidebar.subheader("📚 Phân tích khoảng điểm theo môn")

    danh_sach_mon = {
        "Ngữ Văn": "DTNGUVANIN",
        "Toán": "DTTOANIN",
        "Tiếng Anh": "DTTIENGANHIN"
    }  # Từ điển mapping môn học -> tên cột điểm trong dữ liệu

    mon_chon = st.sidebar.selectbox("Chọn môn",
                                    list(danh_sach_mon.keys()))  # Chọn môn học
    cot_diem_mon = danh_sach_mon[mon_chon]  # Lấy tên cột điểm theo môn chọn

    if cot_diem_mon in du_lieu.columns:  # Kiểm tra cột điểm có trong dữ liệu
        khoang_diem = {
            "0 - 2": (0, 2),
            "Trên 2 - 5": (2, 5),
            "Trên 5 - 8": (5, 8),
            "Trên 8 - 10": (8, 10)
        }  # Định nghĩa các khoảng điểm phân loại

        du_lieu[cot_diem_mon] = pd.to_numeric(
            du_lieu[cot_diem_mon],
            errors='coerce')  # Chuyển điểm sang số, lỗi thành NaN

        def phan_loai_diem(diem):
            if pd.isna(diem):
                return "Vắng"  # Nếu điểm là NaN => học sinh vắng
            for nhan, (duoi, tren) in khoang_diem.items():
                if (duoi == 0 and 0 <= diem <= tren) or (duoi < diem <= tren):
                    return nhan  # Phân loại điểm theo khoảng
            return "Khác"  # Nếu không thuộc khoảng nào

        du_lieu["Khoảng điểm"] = du_lieu[cot_diem_mon].apply(
            phan_loai_diem)  # Tạo cột phân loại điểm

        # Danh sách tất cả khoảng điểm có thể chọn
        tat_ca_khoang = list(khoang_diem.keys()) + ["Vắng"]
        khoang_chon = st.sidebar.multiselect(
            "Chọn khoảng điểm",
            tat_ca_khoang,
            default=tat_ca_khoang)  # Cho phép chọn nhiều khoảng điểm

        # Lọc dữ liệu theo khoảng điểm đã chọn
        du_lieu_loc = du_lieu[du_lieu["Khoảng điểm"].isin(khoang_chon)]

        # Tạo bảng thống kê số lượng học sinh theo khoảng điểm
        bang_thong_ke = du_lieu_loc["Khoảng điểm"].value_counts().reset_index()
        bang_thong_ke.columns = ["Khoảng điểm", "Số lượng"]

        # Định nghĩa thứ tự sắp xếp các khoảng điểm để biểu đồ và bảng hiển thị
        # đúng thứ tự
        thu_tu_bang = {
            "0 - 2": 1,
            "Trên 2 - 5": 2,
            "Trên 5 - 8": 3,
            "Trên 8 - 10": 4,
            "Vắng": 5,
            "Khác": 6}
        bang_thong_ke["Thứ tự"] = bang_thong_ke["Khoảng điểm"].map(
            thu_tu_bang)  # Gán thứ tự sắp xếp
        bang_thong_ke = bang_thong_ke.sort_values("Thứ tự").drop(
            columns=["Thứ tự"])  # Sắp xếp và bỏ cột thứ tự

        st.markdown("#### 📄 Thống kê số lượng theo khoảng điểm")
        # Hiển thị bảng thống kê
        st.dataframe(bang_thong_ke, use_container_width=True)

        # Dữ liệu chuẩn bị cho biểu đồ
        du_lieu_bieu_do = du_lieu_loc["Khoảng điểm"].value_counts(
        ).reset_index()
        du_lieu_bieu_do.columns = ["Khoảng điểm", "Số lượng"]
        du_lieu_bieu_do["Thứ tự"] = du_lieu_bieu_do["Khoảng điểm"].map(
            thu_tu_bang)
        du_lieu_bieu_do = du_lieu_bieu_do.sort_values("Thứ tự")

        cot_1, cot_2 = st.columns(2)  # Tạo 2 cột hiển thị biểu đồ

        with cot_1:
            st.plotly_chart(
                px.bar(
                    du_lieu_bieu_do,
                    x="Khoảng điểm",
                    y="Số lượng",
                    color="Khoảng điểm",
                    title=f"Biểu đồ cột: {mon_chon}",
                    color_discrete_sequence=px.colors.qualitative.Set2),
                use_container_width=True)  # Biểu đồ cột số lượng học sinh theo khoảng điểm

        with cot_2:
            st.plotly_chart(
                px.pie(du_lieu_bieu_do, names="Khoảng điểm", values="Số lượng",
                       title=f"Biểu đồ tròn: {mon_chon}"),
                use_container_width=True
            )  # Biểu đồ tròn tỉ lệ học sinh theo khoảng điểm

        if all(cot in du_lieu_goc.columns for cot in danh_sach_mon.values()):
            # Tính điểm trung bình theo môn trong dữ liệu gốc (tất cả đơn vị)
            diem_trung_binh_goc = {}
            for mon, cot in danh_sach_mon.items():
                diem_trung_binh_goc[mon] = pd.to_numeric(
                    du_lieu_goc[cot], errors='coerce').mean()

            # Tính điểm trung bình theo môn trong dữ liệu đã lọc
            diem_trung_binh_loc = {}
            for mon, cot in danh_sach_mon.items():
                if cot in du_lieu.columns:
                    diem_trung_binh_loc[mon] = pd.to_numeric(
                        du_lieu[cot], errors='coerce').mean()
                else:
                    diem_trung_binh_loc[mon] = np.nan

            # Chuẩn bị dataframe để vẽ biểu đồ sin so sánh
            df_sin_compare = pd.DataFrame({
                "Môn học": list(danh_sach_mon.keys()),
                "Điểm trung bình - Tất cả đơn vị": list(diem_trung_binh_goc.values()),
                "Điểm trung bình - Đã lọc": list(diem_trung_binh_loc.values())
            })

            # Vẽ biểu đồ đường so sánh điểm trung bình
            fig_sin = px.line(
                df_sin_compare,
                x="Môn học",
                y=["Điểm trung bình - Tất cả đơn vị", "Điểm trung bình - Đã lọc"],
                title="So sánh điểm trung bình giữa tất cả đơn vị và dữ liệu đã lọc",
                markers=True,
                labels={"value": "Điểm trung bình", "Môn học": "Môn học"},
            )

            st.plotly_chart(fig_sin, use_container_width=True)
        else:
            st.info(
                "Không đủ dữ liệu để vẽ biểu đồ so sánh điểm trung bình giữa các đơn vị.")

        # Nếu có cột 'DONVI' thì vẽ biểu đồ so sánh theo đơn vị
        if "DONVI" in du_lieu_loc.columns:

            tong_hoc_sinh_theo_don_vi = du_lieu_loc.groupby("DONVI").size().reset_index(
                name="Tổng học sinh")  # Tổng số học sinh theo đơn vị
            so_luong_theo_khoang_va_don_vi = du_lieu_loc.groupby(["DONVI", "Khoảng điểm"]).size(
            ).reset_index(name="Số lượng")  # Số lượng theo đơn vị và khoảng điểm

            du_lieu_ghep = so_luong_theo_khoang_va_don_vi.merge(
                tong_hoc_sinh_theo_don_vi, on="DONVI")  # Ghép bảng tổng và bảng số lượng
            du_lieu_ghep["Tỷ lệ (%)"] = (
                du_lieu_ghep["Số lượng"] / du_lieu_ghep["Tổng học sinh"]) * 100  # Tính tỉ lệ %

            du_lieu_ghep["Thứ tự"] = du_lieu_ghep["Khoảng điểm"].map(
                thu_tu_bang)  # Gán thứ tự
            du_lieu_ghep = du_lieu_ghep.sort_values(
                ["DONVI", "Thứ tự"])  # Sắp xếp theo đơn vị và khoảng điểm

            # Vẽ biểu đồ cột chồng tỷ lệ phần trăm theo khoảng điểm và đơn vị
            bieu_do = px.bar(
                du_lieu_ghep,
                x="DONVI",
                y="Tỷ lệ (%)",
                color="Khoảng điểm",
                category_orders={
                    "Khoảng điểm": thu_tu_bang.keys()},
                title=f"Tỷ lệ % học sinh theo khoảng điểm môn {mon_chon} phân theo Đơn vị",
                labels={
                    "DONVI": "Đơn vị",
                    "Tỷ lệ (%)": "Tỷ lệ học sinh (%)"},
                color_discrete_sequence=px.colors.qualitative.Set2)
            bieu_do.update_layout(barmode='stack')
            st.plotly_chart(bieu_do, use_container_width=True)
        else:
            st.info(
                "Dữ liệu không có cột 'DONVI', không thể hiển thị biểu đồ so sánh theo đơn vị.")
        def tao_pdf_bao_cao(
                bang_thong_ke,
                fig_bar,
                fig_pie,
                fig_compare,
                fig_sin,
                mon_hoc):
            pdf = FPDF()
            pdf.add_page()

            # Thiết lập font
            font_path = "DejaVuSans.ttf"
            bold_font_path = "DejaVuSans-Bold.ttf"
            if os.path.exists(font_path):
                pdf.add_font("DejaVu", "", font_path, uni=True)
                if os.path.exists(bold_font_path):
                    pdf.add_font("DejaVu", "B", bold_font_path, uni=True)
                font_name = "DejaVu"
            else:
                font_name = "Arial"

            # ===== Tiêu đề chính =====
            pdf.set_font(font_name, style="B", size=16)
            pdf.cell(
                0,
                12,
                f"BÁO CÁO PHÂN TÍCH MÔN {mon_hoc.upper()}",
                ln=True,
                align="C")

            pdf.ln(8)

            # ===== Tiêu đề bảng thống kê =====
            pdf.set_font(font_name, style="B", size=11)
            pdf.cell(
                0,
                10,
                "Bảng thống kê theo khoảng điểm",
                ln=True,
                align="C")
            pdf.ln(5)

            # Bảng căn giữa
            pdf.set_font(font_name, size=12)
            col1_w = 60
            col2_w = 40
            table_width = col1_w + col2_w
            x_start = (210 - table_width) / 2
            pdf.set_x(x_start)
            pdf.cell(col1_w, 10, "Khoảng điểm", border=1, align='C')
            pdf.cell(col2_w, 10, "Số lượng", border=1, ln=True, align='C')

            for _, row in bang_thong_ke.iterrows():
                pdf.set_x(x_start)
                pdf.cell(
                    col1_w, 10, str(
                        row["Khoảng điểm"]), border=1, align='C')
                pdf.cell(
                    col2_w, 10, str(
                        row["Số lượng"]), border=1, ln=True, align='C')

            pdf.ln(10)

            # ===== Cập nhật layout trắng cho biểu đồ =====
            for fig in [fig_bar, fig_pie, fig_compare, fig_sin]:
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            fig_pie.update_traces(
                marker=dict(
                    line=dict(
                        color='white',
                        width=2)))
            
            # Hàm lưu biểu đồ tạm
            def save_fig_tmp(fig, prefix="plotly", ext=".png"):
                with tempfile.NamedTemporaryFile(prefix=prefix, suffix=ext, delete=False) as tmp_file:
                    img_bytes = pio.to_image(
                        fig, format="png", width=800, height=500)
                    tmp_file.write(img_bytes)
                    return tmp_file.name

            # Lưu hình ảnh
            img_bar_path = save_fig_tmp(fig_bar, prefix="bar_")
            img_pie_path = save_fig_tmp(fig_pie, prefix="pie_")
            img_compare_path = save_fig_tmp(fig_compare, prefix="compare_")
            img_sin_path = save_fig_tmp(fig_sin, prefix="sin_")

            # Hàm chèn biểu đồ
            def chen_bieu_do(pdf, img_path):
                pdf.set_font(font_name, style="B", size=13)
                pdf.cell(0, 10, ln=True, align="C")
                pdf.ln(4)
                img_width = 180
                x_img = (210 - img_width) / 2
                pdf.image(img_path, x=x_img, w=img_width)
                pdf.ln(12)

            # Chèn các biểu đồ
            chen_bieu_do(pdf, img_bar_path)
            chen_bieu_do(pdf, img_pie_path)
            chen_bieu_do(
                pdf,
                img_compare_path)
            chen_bieu_do(
                pdf,
                img_sin_path)

            # Xoá file tạm
            for path in [
                    img_bar_path,
                    img_pie_path,
                    img_compare_path,
                    img_sin_path]:
                os.remove(path)

            # Xuất PDF ra bytes
            pdf_output = bytes(pdf.output(dest='S'))
            return pdf_output

        if st.button("📄 Tạo báo cáo PDF"):
            # Biểu đồ cột
            fig_bar = px.bar(
                du_lieu_bieu_do,
                x="Khoảng điểm",
                y="Số lượng",
                color="Khoảng điểm",
                category_orders={"Khoảng điểm": thu_tu_bang.keys()},
                title=f"Biểu đồ cột: {mon_chon}",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )

            # Cập nhật style cho tiêu đề
            fig_bar.update_layout(
                title=dict(
                    text=f"<b>Biểu đồ cột: {mon_chon}</b>",  # Thẻ <b> giúp in đậm
                    x=0.5,  # canh giữa tiêu đề
                    xanchor='center'
                )
            )

            # Biểu đồ tròn
            fig_pie = px.pie(
                du_lieu_bieu_do,
                names="Khoảng điểm",
                values="Số lượng",
                title=f"<b>Biểu đồ tròn: {mon_chon}</b>",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_pie.update_layout(
                title=dict(x=0.5, xanchor="center")
            )

            if "DONVI" in du_lieu_loc.columns:
                bieu_do_compare = px.bar(
                    du_lieu_ghep,
                    x="DONVI",
                    y="Tỷ lệ (%)",
                    color="Khoảng điểm",
                    category_orders={"Khoảng điểm": thu_tu_bang.keys()},
                    title=f"<b>Tỷ lệ % học sinh theo khoảng điểm môn {mon_chon} phân theo Đơn vị</b>",
                    labels={"DONVI": "Đơn vị", "Tỷ lệ (%)": "Tỷ lệ học sinh (%)"},
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                bieu_do_compare.update_layout(
                    barmode='stack',
                    xaxis=dict(tickfont=dict(size=8)),
                    title=dict(x=0.5, xanchor="center")
                )
            else:
                bieu_do_compare = px.bar(
                    title="<b>Không có dữ liệu so sánh theo đơn vị</b>")
                bieu_do_compare.update_layout(title=dict(x=0.5, xanchor="center"))

            # Biểu đồ sin so sánh điểm trung bình
            fig_sin = px.line(
                df_sin_compare,
                x="Môn học",
                y=["Điểm trung bình - Tất cả đơn vị", "Điểm trung bình - Đã lọc"],
                title="<b>So sánh điểm trung bình giữa tất cả đơn vị và dữ liệu đã lọc</b>",
                markers=True,
                labels={"value": "Điểm trung bình", "Môn học": "Môn học"},
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_sin.update_layout(
                title=dict(x=0.5, xanchor="center")
            )

            pdf_data = tao_pdf_bao_cao(
                bang_thong_ke,
                fig_bar,
                fig_pie,
                bieu_do_compare,
                fig_sin,
                mon_chon)

            st.download_button(
                label="📥 Tải file PDF báo cáo",
                data=pdf_data,
                file_name="bao_cao_phan_tich_diem.pdf",
                mime="application/pdf",
            )

        st.markdown("---")
        st.subheader("💬 Trợ lý hướng dẫn sử dụng hệ thống phân tích điểm thi")

        # Khởi tạo session_state lưu hội thoại
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Xin chào! Tôi là trợ lý hướng dẫn sử dụng hệ thống phân tích điểm thi. Bạn muốn mình hướng dẫn sử dụng chức năng gì?"}
            ]

        # Hiển thị đoạn hội thoại
        for i, msg in enumerate(st.session_state.messages):
            message(msg["content"], is_user=(msg["role"] == "user"), key=f"msg_{i}")

        # === Hàm phản hồi theo hướng dẫn mở rộng ===
        def guide_bot_reply(text):
            text = text.lower()

            if "tải báo cáo" in text or "pdf" in text or "xuất file" in text:
                return (
                    "📄 Để tải báo cáo:\n"
                    "1. Cuộn xuống cuối trang.\n"
                    "2. Nhấn nút **📥 Tải file PDF báo cáo**.\n"
                    "Hệ thống sẽ tạo một bản báo cáo phân tích chi tiết bạn có thể lưu lại."
                )
            elif "điểm trung bình" in text:
                return (
                    "📊 Để xem điểm trung bình các môn:\n"
                    "1. Hệ thống hiển thị bảng điểm tổng hợp.\n"
                    "2. Dưới bảng có biểu đồ so sánh điểm trung bình giữa các môn.\n"
                    "3. Có thể lọc theo đơn vị, trường, lớp, khối hoặc giới tính để so sánh chi tiết hơn."
                )
            elif "phân tích khoảng điểm" in text or "thống kê" in text:
                return (
                    "📚 Để phân tích khoảng điểm:\n"
                    "1. Chọn một **môn học** trong thanh bên trái.\n"
                    "2. Hệ thống sẽ hiện biểu đồ số lượng học sinh theo từng khoảng điểm.\n"
                    "3. Dùng bộ lọc để phân tích sâu theo đơn vị, trường, lớp hoặc giới tính."
                )
            elif "lọc dữ liệu" in text or "giới tính" in text or "dân tộc" in text:
                return (
                    "🔍 Hướng dẫn lọc dữ liệu:\n"
                    "1. Sử dụng **thanh bên trái** chọn đơn vị, trường, lớp, giới tính, dân tộc.\n"
                    "2. Bảng dữ liệu và biểu đồ sẽ tự động cập nhật theo bộ lọc.\n"
                    "👉 Giúp so sánh giữa các nhóm học sinh dễ dàng hơn."
                )
            elif "bắt đầu" in text or "hướng dẫn" in text:
                return (
                    "🚀 Cách sử dụng cơ bản:\n"
                    "1. Chọn **bộ lọc** bên trái để lọc dữ liệu.\n"
                    "2. Xem **bảng tổng hợp** và biểu đồ phân tích.\n"
                    "3. Dùng **nút tải PDF** để xuất báo cáo nếu cần.\n"
                    "Hãy thử chọn một câu hỏi gợi ý bên dưới nhé!"
                )
            elif "cách nhập dữ liệu" in text or "file" in text:
                return (
                    "🗂️ Cách nhập dữ liệu:\n"
                    "1. Chuẩn bị file Excel hoặc CSV có các cột: DONVI, TRUONG, LOP, GT, DT và điểm các môn.\n"
                    "2. Upload file lên hệ thống qua nút **Chọn file**.\n"
                    "3. Hệ thống tự động đọc và hiển thị dữ liệu để bạn phân tích."
                )
            elif "các môn học" in text or "môn" in text:
                return (
                    "📚 Các môn phân tích:\n"
                    "Hiện hệ thống hỗ trợ phân tích điểm các môn: Ngữ Văn, Toán, Tiếng Anh.\n"
                    "Bạn có thể chọn môn để xem phân tích chi tiết từng môn."
                )
            elif "lỗi" in text or "vấn đề" in text:
                return (
                    "⚠️ Nếu gặp lỗi:\n"
                    "1. Kiểm tra định dạng file đúng (.xlsx hoặc .csv).\n"
                    "2. Đảm bảo các cột bắt buộc có trong file.\n"
                    "3. Thử tải lại file hoặc liên hệ bộ phận hỗ trợ."
                )
            elif "xuất file excel" in text:
                return (
                    "📥 Hệ thống hiện chỉ hỗ trợ xuất báo cáo dạng PDF.\n"
                    "Nếu bạn cần xuất Excel, vui lòng tải dữ liệu lọc dưới dạng CSV riêng."
                )
            else:
                return (
                    "🤖 Xin lỗi, tôi chưa hiểu rõ yêu cầu. Bạn có thể chọn câu hỏi gợi ý bên dưới hoặc hỏi lại rõ hơn nhé!"
                )

        # === Gợi ý câu hỏi thường gặp (mở rộng) ===
        st.markdown("**📌 Hướng dẫn nhanh:**")
        col1, col2 = st.columns(2)

        if "prompt" not in st.session_state:
            st.session_state.prompt = None

        with col1:
            if st.button("📄 Làm sao để tải PDF báo cáo?"):
                st.session_state.prompt = "Tải báo cáo PDF"
            elif st.button("📊 Xem điểm trung bình các môn"):
                st.session_state.prompt = "Điểm trung bình các môn"
            elif st.button("🗂️ Cách nhập dữ liệu?"):
                st.session_state.prompt = "Cách nhập dữ liệu"

        with col2:
            if st.button("📚 Phân tích khoảng điểm môn học"):
                st.session_state.prompt = "Phân tích khoảng điểm"
            elif st.button("🔍 Hướng dẫn lọc"):
                st.session_state.prompt = "Lọc dữ liệu"
            elif st.button("⚠️ Gặp lỗi, sự cố khi sử dụng"):
                st.session_state.prompt = "Lỗi sử dụng"

        # Xử lý tin nhắn nếu có prompt
        prompt = st.session_state.get("prompt", None)

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            reply = guide_bot_reply(prompt)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.prompt = None  # Reset
            st.rerun()
           
