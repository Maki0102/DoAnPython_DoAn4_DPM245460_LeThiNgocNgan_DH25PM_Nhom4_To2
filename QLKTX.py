import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from datetime import date

# =================== Cấu hình và Kết nối MySQL ===================
try:
    # Vui lòng kiểm tra lại thông tin kết nối của bạn
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Maki@0843292719",
        database="qlktx3"
    )
    cursor = conn.cursor()
except mysql.connector.Error as err:
    messagebox.showerror("Lỗi kết nối", f"Không thể kết nối MySQL:\n{err}")
    exit()

# =================== Cấu hình màu sắc ===================
BG_COLOR = "#F0F8FF"  # Màu nền (AliceBlue/Trắng xanh nhạt)
PRIMARY_COLOR = "#007ACC"  # Màu chủ đạo (Xanh dương đậm)
BUTTON_COLOR = "#4CAF50"  # Màu nút (Xanh lá)
BUTTON_FG = "white"
HEADING_COLOR = "#2C3E50"  # Màu chữ tiêu đề

# =================== Tkinter ===================
root = tk.Tk()
root.title("Quản lý Ký túc xá")
root.geometry("1250x650")
root.resizable(False, False)
root.config(bg=BG_COLOR)  # Đặt màu nền cho cửa sổ chính

# =================== Tiêu đề ===================
lbl_title = tk.Label(root, text="QUẢN LÝ KÝ TÚC XÁ", font=("Arial", 16, "bold"), fg=PRIMARY_COLOR, bg=BG_COLOR)
lbl_title.pack(pady=10)


# =======================================================
# =========== CÁC HÀM TIỆN ÍCH VÀ LOGIC ỨNG DỤNG =========
# =======================================================

# ================== Hàm tiện ích CURRENCY ==================

def format_currency(number):
    if number is None:
        return ""
    try:
        return "{:,.0f}".format(float(number)).replace(",", ".")
    except (ValueError, TypeError):
        return str(number)


def parse_currency(currency_str):
    if not currency_str:
        return 0
    try:
        cleaned_str = str(currency_str).replace('.', '').replace(',', '').strip()
        if not cleaned_str:
            return 0
        return int(float(cleaned_str))
    except ValueError:
        raise ValueError("Tiền phòng phải là một số hợp lệ.")


# ================== Hàm tiện ích KHÁC ==================
def get_selected_ma_sv():
    ma_sv = entry_ma_so.get().strip()
    return ma_sv if entry_ma_so['state'] == tk.DISABLED else None


def load_data(sql_query=None, params=None):
    for item in tree.get_children():
        tree.delete(item)

    if sql_query is None:
        sql_query = "SELECT MaSV, Ten, HoTen, GioiTinh, NgaySinh, MaPhong, NgayVao, NgayRa, TienPhong, TrangThai, TrangThaiDongTien FROM quanlyktx"

    try:
        cursor.execute(sql_query, params or ())
        records = cursor.fetchall()

        for record in records:
            ma_sv, ten, ho_ten, gioi_tinh, ngay_sinh, ma_phong, ngay_vao, ngay_ra, tien_phong, trang_thai, trang_thai_dong_tien = record

            ngay_sinh_str = ngay_sinh.strftime("%m/%d/%y") if ngay_sinh else ""
            ngay_vao_str = ngay_vao.strftime("%m/%d/%y") if ngay_vao else ""
            ngay_ra_str = ngay_ra.strftime("%m/%d/%y") if ngay_ra else ""
            tien_phong_str = format_currency(tien_phong)

            tree.insert("", "end",
                        values=(ma_sv, ho_ten, ten, gioi_tinh, ngay_sinh_str, ma_phong, ngay_vao_str, ngay_ra_str,
                                tien_phong_str, trang_thai, trang_thai_dong_tien))

        if params is not None:
            messagebox.showinfo("Tìm kiếm", f"Tìm thấy {len(records)} kết quả.")

    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi MySQL", f"Không thể tải dữ liệu:\n{err}")
    except Exception as e:
        print(f"Lỗi tải dữ liệu: {e}")


def clear_entries():
    """Xóa các trường nhập liệu và đặt lại các giá trị mặc định."""
    entry_ma_so.config(state=tk.NORMAL)
    entry_ma_so.delete(0, tk.END)
    entry_ho_ten.delete(0, tk.END)
    entry_ten.delete(0, tk.END)
    phai_var.set("Nam")
    cal_ngay_sinh.set_date(date.today())

    combo_ma_phong.set("")
    cal_ngay_vao.set_date(date.today())
    cal_ngay_ra.set_date(date.today())
    entry_tien_phong.delete(0, tk.END)
    combo_trang_thai.set("")
    combo_dong_tien.set("Chưa đóng")

    entry_search.delete(0, tk.END)
    load_data()


# ================== Hàm Tìm kiếm ==================

def search_data():
    """Tìm kiếm sinh viên theo từ khóa trong các cột MaSV, HoTen, Ten, MaPhong."""
    search_term = entry_search.get().strip()
    if not search_term:
        messagebox.showwarning("Tìm kiếm", "Vui lòng nhập từ khóa tìm kiếm!")
        load_data()
        return

    like_term = f"%{search_term}%"

    sql = """
          SELECT MaSV, \
                 Ten, \
                 HoTen, \
                 GioiTinh, \
                 NgaySinh, \
                 MaPhong, \
                 NgayVao, \
                 NgayRa, \
                 TienPhong, \
                 TrangThai, \
                 TrangThaiDongTien
          FROM quanlyktx
          WHERE MaSV LIKE %s \
             OR HoTen LIKE %s \
             OR Ten LIKE %s \
             OR MaPhong LIKE %s
          """
    params = (like_term, like_term, like_term, like_term)

    load_data(sql, params)


# ================== Hàm CRUD ==================

def add_record():
    ma_sv = entry_ma_so.get().strip()
    ho_ten = entry_ho_ten.get().strip()
    ten = entry_ten.get().strip()
    gioi_tinh = phai_var.get()
    ngay_sinh = cal_ngay_sinh.get_date()
    ma_phong = combo_ma_phong.get().strip()
    ngay_vao = cal_ngay_vao.get_date()
    ngay_ra_val = cal_ngay_ra.get_date() if cal_ngay_ra.get() else None
    trang_thai = combo_trang_thai.get()
    trang_thai_dong_tien = combo_dong_tien.get()

    if ma_sv == "":
        messagebox.showwarning("Chú ý", "Mã sinh viên không được để trống!")
        return

    try:
        tien_phong = parse_currency(entry_tien_phong.get())
    except ValueError as e:
        messagebox.showwarning("Lỗi nhập liệu", str(e))
        return

    if not ma_phong or not trang_thai or not trang_thai_dong_tien:
        messagebox.showwarning("Chú ý", "Mã phòng, Trạng thái và Trạng thái đóng tiền không được để trống!")
        return

    try:
        cursor.execute("SELECT MaSV FROM quanlyktx WHERE MaSV = %s", (ma_sv,))
        if cursor.fetchone():
            messagebox.showwarning("Cảnh báo", f"Mã sinh viên {ma_sv} đã tồn tại!")
            return

        sql = """
              INSERT INTO quanlyktx (MaSV, Ten, HoTen, GioiTinh, NgaySinh, MaPhong, NgayVao, NgayRa, TienPhong,
                                     TrangThai, TrangThaiDongTien)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              """
        val = (ma_sv, ten, ho_ten, gioi_tinh, ngay_sinh, ma_phong, ngay_vao, ngay_ra_val, tien_phong, trang_thai,
               trang_thai_dong_tien)
        cursor.execute(sql, val)
        conn.commit()
        messagebox.showinfo("Thành công", "Thêm dữ liệu KTX thành công!")
        load_data()
        clear_entries()
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi MySQL", f"Không thể thêm dữ liệu:\n{err}")


def edit_record():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Chú ý", "Vui lòng chọn một sinh viên để sửa.")
        return
    messagebox.showinfo("Thông báo", "Vui lòng chỉnh sửa dữ liệu trong các ô nhập liệu và nhấn 'Lưu'.")


def save_record():
    ma_sv_hien_tai = get_selected_ma_sv()
    if not ma_sv_hien_tai:
        messagebox.showwarning("Chú ý", "Vui lòng chọn hoặc điền Mã SV hợp lệ trước khi Lưu/Sửa.")
        return

    ho_ten = entry_ho_ten.get().strip()
    ten = entry_ten.get().strip()
    gioi_tinh = phai_var.get()
    ngay_sinh = cal_ngay_sinh.get_date()
    ma_phong = combo_ma_phong.get().strip()
    ngay_vao = cal_ngay_vao.get_date()
    ngay_ra_val = cal_ngay_ra.get_date() if cal_ngay_ra.get() else None
    trang_thai = combo_trang_thai.get()
    trang_thai_dong_tien = combo_dong_tien.get()

    if not ho_ten or not ten or not ma_phong or not trang_thai or not trang_thai_dong_tien:
        messagebox.showwarning("Chú ý",
                               "Các trường Họ tên, Tên, Mã phòng, Trạng thái và Trạng thái đóng tiền không được để trống.")
        return

    try:
        tien_phong = parse_currency(entry_tien_phong.get())
    except ValueError as e:
        messagebox.showwarning("Lỗi nhập liệu", str(e))
        return

    try:
        sql = """
              UPDATE quanlyktx
              SET HoTen             = %s,
                  Ten               = %s,
                  GioiTinh          = %s,
                  NgaySinh          = %s,
                  MaPhong           = %s,
                  NgayVao           = %s,
                  NgayRa            = %s,
                  TienPhong         = %s,
                  TrangThai         = %s,
                  TrangThaiDongTien = %s
              WHERE MaSV = %s \
              """
        val = (ho_ten, ten, gioi_tinh, ngay_sinh, ma_phong,
               ngay_vao, ngay_ra_val, tien_phong, trang_thai, trang_thai_dong_tien, ma_sv_hien_tai)

        cursor.execute(sql, val)
        conn.commit()

        if cursor.rowcount > 0:
            messagebox.showinfo("Thành công", f"Cập nhật sinh viên {ma_sv_hien_tai} thành công!")
            load_data()
            clear_entries()
        else:
            messagebox.showwarning("Cảnh báo", f"Không tìm thấy sinh viên có Mã SV: {ma_sv_hien_tai} để cập nhật.")

    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi MySQL", f"Không thể cập nhật dữ liệu:\n{err}")


def delete_record():
    ma_sv_hien_tai = get_selected_ma_sv()
    if not ma_sv_hien_tai:
        messagebox.showwarning("Chú ý", "Vui lòng chọn một sinh viên để xóa.")
        return

    if messagebox.askyesno("Xác nhận Xóa", f"Bạn có chắc chắn muốn xóa sinh viên có Mã SV: {ma_sv_hien_tai} không?"):
        try:
            cursor.execute("DELETE FROM quanlyktx WHERE MaSV = %s", (ma_sv_hien_tai,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Thành công", "Xóa sinh viên thành công!")
                load_data()
                clear_entries()
            else:
                messagebox.showwarning("Cảnh báo", f"Không tìm thấy sinh viên có Mã SV: {ma_sv_hien_tai} để xóa.")
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi MySQL", f"Không thể xóa dữ liệu:\n{err}")


def select_record(event):
    selected = tree.focus()
    if selected:
        values = tree.item(selected, 'values')
        if values:
            clear_entries()
            ma_sv, ho_ten, ten, gioi_tinh, ngay_sinh_str, ma_phong, ngay_vao_str, ngay_ra_str, tien_phong, trang_thai, trang_thai_dong_tien = values

            entry_ma_so.config(state=tk.NORMAL)
            entry_ma_so.insert(0, ma_sv)
            entry_ma_so.config(state=tk.DISABLED)

            entry_ho_ten.insert(0, ho_ten)
            entry_ten.insert(0, ten)
            phai_var.set(gioi_tinh)
            cal_ngay_sinh.set_date(ngay_sinh_str)

            combo_ma_phong.set(ma_phong)
            cal_ngay_vao.set_date(ngay_vao_str)
            cal_ngay_ra.set_date(ngay_ra_str)

            entry_tien_phong.insert(0, tien_phong)

            combo_trang_thai.set(trang_thai)
            combo_dong_tien.set(trang_thai_dong_tien)


def exit_app():
    if conn.is_connected():
        conn.close()
    root.quit()


# =======================================================
# =================== XÂY DỰNG GIAO DIỆN ==================
# =======================================================

# --- Cấu hình màu cho Label và RadioButton ---
label_config = {"bg": BG_COLOR, "fg": HEADING_COLOR}
radio_config = {"bg": BG_COLOR, "fg": HEADING_COLOR, "selectcolor": BG_COLOR}

# ================== Frame nhập dữ liệu (Top Frame) ==================
frame_input = tk.Frame(root, padx=10, pady=10, bg=BG_COLOR)
frame_input.pack(side=tk.TOP, fill=tk.X)
frame_grid = tk.Frame(frame_input, bg=BG_COLOR)
frame_grid.pack(expand=True)
INPUT_WIDTH = 20

# Hàng 1: Mã SV | Mã phòng
tk.Label(frame_grid, text="Mã SV", **label_config).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
entry_ma_so = tk.Entry(frame_grid, width=INPUT_WIDTH)
entry_ma_so.grid(row=0, column=1, padx=(0, 50), pady=5, sticky="w")
tk.Label(frame_grid, text="Mã phòng", **label_config).grid(row=0, column=2, padx=(0, 10), pady=5, sticky="w")
phong_list = [f"P{i:03d}" for i in range(101, 401)]
combo_ma_phong = ttk.Combobox(frame_grid, values=phong_list, state="readonly", width=INPUT_WIDTH - 2)
combo_ma_phong.grid(row=0, column=3, padx=5, pady=5, sticky="w")
combo_ma_phong.set("")

# Hàng 2-6 (Họ tên, Tên, Phái, Ngày sinh, Ngày vào, Ngày ra, Tiền phòng, Trạng thái, Đóng tiền)
tk.Label(frame_grid, text="Họ tên", **label_config).grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
entry_ho_ten = tk.Entry(frame_grid, width=INPUT_WIDTH)
entry_ho_ten.grid(row=1, column=1, padx=(0, 50), pady=5, sticky="w")
tk.Label(frame_grid, text="Tên", **label_config).grid(row=1, column=2, padx=(0, 10), pady=5, sticky="w")
entry_ten = tk.Entry(frame_grid, width=INPUT_WIDTH)
entry_ten.grid(row=1, column=3, padx=5, pady=5, sticky="w")
tk.Label(frame_grid, text="Phái", **label_config).grid(row=2, column=0, padx=(0, 10), pady=5, sticky="w")
phai_var = tk.StringVar(value="Nam")
radio_nam = tk.Radiobutton(frame_grid, text="Nam", variable=phai_var, value="Nam", **radio_config)
radio_nam.grid(row=2, column=1, padx=(0, 50), pady=5, sticky="w")
radio_nu = tk.Radiobutton(frame_grid, text="Nữ", variable=phai_var, value="Nữ", **radio_config)
radio_nu.grid(row=2, column=1, padx=(60, 50), pady=5, sticky="w")
tk.Label(frame_grid, text="Ngày sinh", **label_config).grid(row=2, column=2, padx=(0, 10), pady=5, sticky="w")
cal_ngay_sinh = DateEntry(frame_grid, width=INPUT_WIDTH - 2, background=PRIMARY_COLOR,
                          foreground='white', borderwidth=2, date_pattern='mm/dd/yy')
cal_ngay_sinh.grid(row=2, column=3, padx=5, pady=5, sticky="w")
tk.Label(frame_grid, text="Ngày vào", **label_config).grid(row=3, column=0, padx=(0, 10), pady=5, sticky="w")
cal_ngay_vao = DateEntry(frame_grid, width=INPUT_WIDTH - 2, background=PRIMARY_COLOR,
                         foreground='white', borderwidth=2, date_pattern='mm/dd/yy')
cal_ngay_vao.grid(row=3, column=1, padx=(0, 50), pady=5, sticky="w")
tk.Label(frame_grid, text="Ngày ra", **label_config).grid(row=3, column=2, padx=(0, 10), pady=5, sticky="w")
cal_ngay_ra = DateEntry(frame_grid, width=INPUT_WIDTH - 2, background=PRIMARY_COLOR,
                        foreground='white', borderwidth=2, date_pattern='mm/dd/yy')
cal_ngay_ra.grid(row=3, column=3, padx=5, pady=5, sticky="w")
tk.Label(frame_grid, text="Tiền phòng", **label_config).grid(row=4, column=0, padx=(0, 10), pady=5, sticky="w")
entry_tien_phong = tk.Entry(frame_grid, width=INPUT_WIDTH)
entry_tien_phong.grid(row=4, column=1, padx=(0, 50), pady=5, sticky="w")
tk.Label(frame_grid, text="Trạng thái", **label_config).grid(row=4, column=2, padx=(0, 10), pady=5, sticky="w")
trang_thai_list = ["Đang ở", "Đã rời", "Chờ xếp phòng",
                   "Tạm nghỉ"]
combo_trang_thai = ttk.Combobox(frame_grid, values=trang_thai_list, state="readonly", width=INPUT_WIDTH - 2)
combo_trang_thai.grid(row=4, column=3, padx=5, pady=5, sticky="w")
combo_trang_thai.set("")
tk.Label(frame_grid, text="Đóng tiền", **label_config).grid(row=5, column=0, padx=(0, 10), pady=5, sticky="w")
dong_tien_list = ["Đã đóng", "Chưa đóng"]
combo_dong_tien = ttk.Combobox(frame_grid, values=dong_tien_list, state="readonly", width=INPUT_WIDTH - 2)
combo_dong_tien.grid(row=5, column=1, padx=(0, 50), pady=5, sticky="w")
combo_dong_tien.set("Chưa đóng")

# --- Các Nút Thao tác ---
frame_buttons = tk.Frame(root, padx=10, pady=10, bg=BG_COLOR)
frame_buttons.pack(side=tk.TOP, fill=tk.X)
frame_button_center = tk.Frame(frame_buttons, bg=BG_COLOR)
frame_button_center.pack(expand=True)
button_style = {"bg": BUTTON_COLOR, "fg": BUTTON_FG, "width": 10}

btn_add = tk.Button(frame_button_center, text="Thêm", command=add_record, **button_style)
btn_add.pack(side=tk.LEFT, padx=5)
btn_save = tk.Button(frame_button_center, text="Lưu", command=save_record, **button_style)
btn_save.pack(side=tk.LEFT, padx=5)
btn_edit = tk.Button(frame_button_center, text="Sửa", command=edit_record, **button_style)
btn_edit.pack(side=tk.LEFT, padx=5)
btn_cancel = tk.Button(frame_button_center, text="Hủy", command=clear_entries, **button_style)
btn_cancel.pack(side=tk.LEFT, padx=5)
btn_delete = tk.Button(frame_button_center, text="Xóa", command=delete_record, **button_style)
btn_delete.pack(side=tk.LEFT, padx=5)
btn_exit = tk.Button(frame_button_center, text="Thoát", command=exit_app, **button_style)
btn_exit.pack(side=tk.LEFT, padx=5)

# ================== Khung Tìm kiếm (ĐÃ CĂN GIỮA) ==================
frame_search = tk.Frame(root, padx=10, bg=BG_COLOR)
frame_search.pack(pady=5, anchor="w", fill=tk.X)

# Frame con để căn giữa các widget tìm kiếm
frame_search_center = tk.Frame(frame_search, bg=BG_COLOR)
frame_search_center.pack(expand=True)

tk.Label(frame_search_center, text="Tìm kiếm (Mã SV, Tên, Phòng):", **label_config).pack(side=tk.LEFT, padx=(0, 5))
entry_search = tk.Entry(frame_search_center, width=30)
entry_search.pack(side=tk.LEFT, padx=(0, 10))

btn_search = tk.Button(frame_search_center, text="Tìm kiếm 🔍", command=search_data, bg=PRIMARY_COLOR, fg=BUTTON_FG,
                       width=15)
btn_search.pack(side=tk.LEFT, padx=5)

# --- Tiêu đề Danh sách sinh viên KTX ---
tk.Label(root, text="Danh sách sinh viên KTX", font=("Arial", 12), bg=BG_COLOR, fg=PRIMARY_COLOR).pack(pady=5,
                                                                                                       anchor="w",
                                                                                                       padx=10)

# ================== Frame bảng dữ liệu (Treeview - Cột KTX) ==================
frame_table = tk.Frame(root)
frame_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Cấu hình Treeview Style
style = ttk.Style()
# Màu chữ tiêu đề bảng là MÀU ĐEN
style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background=PRIMARY_COLOR, foreground='black')
style.configure("Treeview", background="white", foreground="black", rowheight=25)
style.map('Treeview', background=[('selected', '#B0E0E6')])

# Định nghĩa các cột
columns = ("MaSV", "HoTen", "Ten", "GioiTinh", "NgaySinh", "MaPhong", "NgayVao", "NgayRa", "TienPhong", "TrangThai",
           "DongTien")
tree = ttk.Treeview(frame_table, columns=columns, show="headings")

# Thanh cuộn dọc
scrollbar_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar_y.set)
scrollbar_y.pack(side="right", fill="y")

# Thiết lập Heading và Column Width
tree.heading("MaSV", text="Mã SV")
tree.column("MaSV", width=70, anchor=tk.CENTER)
tree.heading("HoTen", text="Họ tên")
tree.column("HoTen", width=120)
tree.heading("Ten", text="Tên")
tree.column("Ten", width=70)
tree.heading("GioiTinh", text="GT")
tree.column("GioiTinh", width=40, anchor=tk.CENTER)
tree.heading("NgaySinh", text="Ngày sinh")
tree.column("NgaySinh", width=90, anchor=tk.CENTER)
tree.heading("MaPhong", text="Mã phòng")
tree.column("MaPhong", width=80, anchor=tk.CENTER)
tree.heading("NgayVao", text="Ngày vào")
tree.column("NgayVao", width=90, anchor=tk.CENTER)
tree.heading("NgayRa", text="Ngày ra")
tree.column("NgayRa", width=90, anchor=tk.CENTER)
tree.heading("TienPhong", text="Tiền phòng")
tree.column("TienPhong", width=100, anchor=tk.CENTER)
tree.heading("TrangThai", text="Trạng thái")
tree.column("TrangThai", width=100)
tree.heading("DongTien", text="Đóng tiền")
tree.column("DongTien", width=90, anchor=tk.CENTER)

tree.pack(fill=tk.BOTH, expand=True)

# Gắn sự kiện click vào Treeview
tree.bind("<<TreeviewSelect>>", select_record)

# Tải dữ liệu KTX khi ứng dụng khởi động
load_data()

# ================== Chạy ứng dụng ==================
root.protocol("WM_DELETE_WINDOW", exit_app)
root.mainloop()