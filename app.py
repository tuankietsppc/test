import streamlit as st # type: ignore
import pandas as pd # type: ignore
import plotly.express as px # type: ignore
import numpy as np # type: ignore
import io
import os
from fpdf import FPDF # type: ignore
import plotly.io as pio # type: ignore
import tempfile

# Thiết lập tiêu đề và bố cục trang
st.set_page_config(page_title='Phân tích điểm thi', layout="wide")  # Đặt tiêu đề trang và chế độ bố cục rộng
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
tep_tai_len = st.file_uploader('📤 Chọn file Excel', type='xlsx')  # Tải lên file Excel

if tep_tai_len:
    du_lieu = pd.read_excel(tep_tai_len, engine='openpyxl')  # Đọc dữ liệu Excel
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
            du_lieu_don_vi = du_lieu_don_vi[du_lieu_don_vi["DONVI"] == don_vi_chon]

        # Lọc Trường (sau khi lọc đơn vị)
        ds_truong = du_lieu_don_vi["TRUONG"].dropna().unique().tolist()
        ds_truong.insert(0, "Tất cả")
        truong_chon = st.sidebar.selectbox("Chọn trường", ds_truong)

        du_lieu_truong = du_lieu_don_vi.copy()
        if truong_chon != "Tất cả":
            du_lieu_truong = du_lieu_truong[du_lieu_truong["TRUONG"] == truong_chon]

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
            gioi_tinh_chon = st.sidebar.selectbox("Chọn giới tính", ds_gioi_tinh)

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
        st.warning("Không tìm thấy đủ các cột 'DONVI', 'TRUONG', 'LOP' trong file Excel.")  # Cảnh báo nếu thiếu cột

    # === HIỂN THỊ DỮ LIỆU SAU LỌC ===
    st.dataframe(du_lieu)  # Hiển thị bảng dữ liệu đã lọc
    so_dong_du_lieu = du_lieu.shape[0]  # Lấy số dòng dữ liệu
    st.write(f"Số dòng của bảng là: {so_dong_du_lieu}")  # Hiển thị số dòng

    

    # === PHÂN TÍCH KHOẢNG ĐIỂM CÁC MÔN ===
    st.sidebar.markdown("---")  # Dòng kẻ ngăn cách trong sidebar
    st.sidebar.subheader("📚 Phân tích khoảng điểm theo môn")  # Tiêu đề phụ trong sidebar

    danh_sach_mon = {
        "Ngữ Văn": "DTNGUVANIN",
        "Toán": "DTTOANIN",
        "Tiếng Anh": "DTTIENGANHIN"
    }  # Từ điển mapping môn học -> tên cột điểm trong dữ liệu

    mon_chon = st.sidebar.selectbox("Chọn môn", list(danh_sach_mon.keys()))  # Chọn môn học
    cot_diem_mon = danh_sach_mon[mon_chon]  # Lấy tên cột điểm theo môn chọn

    if cot_diem_mon in du_lieu.columns:  # Kiểm tra cột điểm có trong dữ liệu
        khoang_diem = {
            "0 - 2": (0, 2),
            "Trên 2 - 5": (2, 5),
            "Trên 5 - 8": (5, 8),
            "Trên 8 - 10": (8, 10)
        }  # Định nghĩa các khoảng điểm phân loại

        du_lieu[cot_diem_mon] = pd.to_numeric(du_lieu[cot_diem_mon], errors='coerce')  # Chuyển điểm sang số, lỗi thành NaN

        def phan_loai_diem(diem):
            if pd.isna(diem):
                return "Vắng"  # Nếu điểm là NaN => học sinh vắng
            for nhan, (duoi, tren) in khoang_diem.items():
                if (duoi == 0 and 0 <= diem <= tren) or (duoi < diem <= tren):
                    return nhan  # Phân loại điểm theo khoảng
            return "Khác"  # Nếu không thuộc khoảng nào

        du_lieu["Khoảng điểm"] = du_lieu[cot_diem_mon].apply(phan_loai_diem)  # Tạo cột phân loại điểm

        tat_ca_khoang = list(khoang_diem.keys()) + ["Vắng"]  # Danh sách tất cả khoảng điểm có thể chọn
        khoang_chon = st.sidebar.multiselect("Chọn khoảng điểm", tat_ca_khoang, default=tat_ca_khoang)  # Cho phép chọn nhiều khoảng điểm

        du_lieu_loc = du_lieu[du_lieu["Khoảng điểm"].isin(khoang_chon)]  # Lọc dữ liệu theo khoảng điểm đã chọn


        # Tạo bảng thống kê số lượng học sinh theo khoảng điểm
        bang_thong_ke = du_lieu_loc["Khoảng điểm"].value_counts().reset_index()
        bang_thong_ke.columns = ["Khoảng điểm", "Số lượng"]

        # Định nghĩa thứ tự sắp xếp các khoảng điểm để biểu đồ và bảng hiển thị đúng thứ tự
        thu_tu_bang = {
            "0 - 2": 1, "Trên 2 - 5": 2, "Trên 5 - 8": 3, "Trên 8 - 10": 4, "Vắng": 5, "Khác": 6
        }
        bang_thong_ke["Thứ tự"] = bang_thong_ke["Khoảng điểm"].map(thu_tu_bang)  # Gán thứ tự sắp xếp
        bang_thong_ke = bang_thong_ke.sort_values("Thứ tự").drop(columns=["Thứ tự"])  # Sắp xếp và bỏ cột thứ tự

        st.markdown("#### 📄 Thống kê số lượng theo khoảng điểm")
        st.dataframe(bang_thong_ke, use_container_width=True)  # Hiển thị bảng thống kê

        # Dữ liệu chuẩn bị cho biểu đồ
        du_lieu_bieu_do = du_lieu_loc["Khoảng điểm"].value_counts().reset_index()
        du_lieu_bieu_do.columns = ["Khoảng điểm", "Số lượng"]
        du_lieu_bieu_do["Thứ tự"] = du_lieu_bieu_do["Khoảng điểm"].map(thu_tu_bang)
        du_lieu_bieu_do = du_lieu_bieu_do.sort_values("Thứ tự")

        cot_1, cot_2 = st.columns(2)  # Tạo 2 cột hiển thị biểu đồ

        with cot_1:
            st.plotly_chart(
                px.bar(du_lieu_bieu_do, x="Khoảng điểm", y="Số lượng", color="Khoảng điểm",
                       title=f"Biểu đồ cột: {mon_chon}", color_discrete_sequence=px.colors.qualitative.Set2),
                use_container_width=True
            )  # Biểu đồ cột số lượng học sinh theo khoảng điểm

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
                diem_trung_binh_goc[mon] = pd.to_numeric(du_lieu_goc[cot], errors='coerce').mean()

            # Tính điểm trung bình theo môn trong dữ liệu đã lọc
            diem_trung_binh_loc = {}
            for mon, cot in danh_sach_mon.items():
                if cot in du_lieu.columns:
                    diem_trung_binh_loc[mon] = pd.to_numeric(du_lieu[cot], errors='coerce').mean()
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
            st.info("Không đủ dữ liệu để vẽ biểu đồ so sánh điểm trung bình giữa các đơn vị.")


        
        # Nếu có cột 'DONVI' thì vẽ biểu đồ so sánh theo đơn vị
        if "DONVI" in du_lieu_loc.columns:

            tong_hoc_sinh_theo_don_vi = du_lieu_loc.groupby("DONVI").size().reset_index(name="Tổng học sinh")  # Tổng số học sinh theo đơn vị
            so_luong_theo_khoang_va_don_vi = du_lieu_loc.groupby(["DONVI", "Khoảng điểm"]).size().reset_index(name="Số lượng")  # Số lượng theo đơn vị và khoảng điểm

            du_lieu_ghep = so_luong_theo_khoang_va_don_vi.merge(tong_hoc_sinh_theo_don_vi, on="DONVI")  # Ghép bảng tổng và bảng số lượng
            du_lieu_ghep["Tỷ lệ (%)"] = (du_lieu_ghep["Số lượng"] / du_lieu_ghep["Tổng học sinh"]) * 100  # Tính tỉ lệ %

            du_lieu_ghep["Thứ tự"] = du_lieu_ghep["Khoảng điểm"].map(thu_tu_bang)  # Gán thứ tự
            du_lieu_ghep = du_lieu_ghep.sort_values(["DONVI", "Thứ tự"])  # Sắp xếp theo đơn vị và khoảng điểm

            # Vẽ biểu đồ cột chồng tỷ lệ phần trăm theo khoảng điểm và đơn vị
            bieu_do = px.bar(
                du_lieu_ghep,
                x="DONVI",
                y="Tỷ lệ (%)",
                color="Khoảng điểm",
                category_orders={"Khoảng điểm": thu_tu_bang.keys()},
                title=f"Tỷ lệ % học sinh theo khoảng điểm môn {mon_chon} phân theo Đơn vị",
                labels={"DONVI": "Đơn vị", "Tỷ lệ (%)": "Tỷ lệ học sinh (%)"},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            bieu_do.update_layout(barmode='stack')
            st.plotly_chart(bieu_do, use_container_width=True)
        else:
            st.info("Dữ liệu không có cột 'DONVI', không thể hiển thị biểu đồ so sánh theo đơn vị.")
       
        def tao_pdf_bao_cao(bang_thong_ke, fig_bar, fig_pie, fig_compare, fig_sin, mon_hoc):
            pdf = FPDF()
            pdf.add_page()

            # Cấu hình font
            font_path = "DejaVuSans.ttf"
            if os.path.exists(font_path):
                pdf.add_font("DejaVu", "", font_path, uni=True)
                pdf.set_font("DejaVu", size=14)
                font_name = "DejaVu"
            else:
                pdf.set_font("Arial", size=14)
                font_name = "Arial"

            # Tiêu đề căn giữa
            pdf.cell(0, 10, f"Báo cáo thống kê môn {mon_hoc}", ln=True, align="C")
            pdf.ln(10)

            # Bảng thống kê căn giữa
            pdf.set_font(font_name, size=12)
            col1_w = 60
            col2_w = 40
            total_table_width = col1_w + col2_w
            x_start = (210 - total_table_width) / 2
            pdf.set_x(x_start)
            pdf.cell(col1_w, 10, "Khoảng điểm", border=1, align='C')
            pdf.cell(col2_w, 10, "Số lượng", border=1, ln=True, align='C')

            for _, row in bang_thong_ke.iterrows():
                pdf.set_x(x_start)
                pdf.cell(col1_w, 10, str(row["Khoảng điểm"]), border=1, align='C')
                pdf.cell(col2_w, 10, str(row["Số lượng"]), border=1, ln=True, align='C')

            pdf.ln(10)

            # Đặt nền trắng cho biểu đồ
            for fig in [fig_bar, fig_pie, fig_compare, fig_sin]:
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            fig_pie.update_traces(marker=dict(line=dict(color='white', width=2)))

            # Hàm lưu biểu đồ thành ảnh
            def save_fig_tmp(fig, prefix="plotly", ext=".png"):
                with tempfile.NamedTemporaryFile(prefix=prefix, suffix=ext, delete=False) as tmp_file:
                    img_bytes = pio.to_image(fig, format="png", width=800, height=500)
                    tmp_file.write(img_bytes)
                    return tmp_file.name

            # Lưu hình
            img_bar_path = save_fig_tmp(fig_bar, prefix="bar_")
            img_pie_path = save_fig_tmp(fig_pie, prefix="pie_")
            img_compare_path = save_fig_tmp(fig_compare, prefix="compare_")
            img_sin_path = save_fig_tmp(fig_sin, prefix="sin_")

            # Hàm chèn biểu đồ với tiêu đề căn giữa
            def chen_bieu_do(pdf, title, img_path):
                pdf.set_font(font_name, size=12)
                pdf.cell(0, 10, title, ln=True, align="C")
                pdf.ln(3)
                img_width = 180
                x_img = (210 - img_width) / 2
                pdf.image(img_path, x=x_img, w=img_width)
                pdf.ln(10)

            # Chèn các biểu đồ
            chen_bieu_do(pdf, "Biểu đồ cột", img_bar_path)
            chen_bieu_do(pdf, "Biểu đồ tròn", img_pie_path)
            chen_bieu_do(pdf, "Biểu đồ so sánh tỷ lệ học sinh theo đơn vị", img_compare_path)
            chen_bieu_do(pdf, "Biểu đồ so sánh điểm trung bình giữa tất cả đơn vị và dữ liệu đã lọc", img_sin_path)

            # Xoá file ảnh tạm
            for path in [img_bar_path, img_pie_path, img_compare_path, img_sin_path]:
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

            # Biểu đồ tròn
            fig_pie = px.pie(
                du_lieu_bieu_do,
                names="Khoảng điểm",
                values="Số lượng",
                title=f"Biểu đồ tròn: {mon_chon}",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )

            # Biểu đồ so sánh tỷ lệ theo đơn vị
            if "DONVI" in du_lieu_loc.columns:
                bieu_do_compare = px.bar(
                    du_lieu_ghep,
                    x="DONVI",
                    y="Tỷ lệ (%)",
                    color="Khoảng điểm",
                    category_orders={"Khoảng điểm": thu_tu_bang.keys()},
                    title=f"Tỷ lệ % học sinh theo khoảng điểm môn {mon_chon} phân theo Đơn vị",
                    labels={"DONVI": "Đơn vị", "Tỷ lệ (%)": "Tỷ lệ học sinh (%)"},
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                bieu_do_compare.update_layout(barmode='stack', xaxis=dict(tickfont=dict(size=8)))
            else:
                bieu_do_compare = px.bar(title="Không có dữ liệu so sánh theo đơn vị")

            # Biểu đồ sin so sánh điểm trung bình
            fig_sin = px.line(
                df_sin_compare,
                x="Môn học",
                y=["Điểm trung bình - Tất cả đơn vị", "Điểm trung bình - Đã lọc"],
                title="So sánh điểm trung bình giữa tất cả đơn vị và dữ liệu đã lọc",
                markers=True,
                labels={"value": "Điểm trung bình", "Môn học": "Môn học"},
                color_discrete_sequence=px.colors.qualitative.Set2,
            )

            pdf_data = tao_pdf_bao_cao(bang_thong_ke, fig_bar, fig_pie, bieu_do_compare, fig_sin, mon_chon)

            st.download_button(
                label="📥 Tải file PDF báo cáo",
                data=pdf_data,
                file_name="bao_cao_phan_tich_diem.pdf",
                mime="application/pdf",
            )

