import tkinter as tk
from tkinter import messagebox
import mysql.connector

# =================== Hàm căn giữa cửa sổ ===================
def center_window(win, width, height):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

# =================== Kết nối MySQL ===================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Maki@0843292719",
    database="qlktx3"
)
cursor = conn.cursor()

# =================== Các hàm xử lý ===================
def hien_sinhvien():
    """Hiển thị tất cả sinh viên lên Listbox"""
    listbox.delete(0, tk.END)
    cursor.execute("SELECT * FROM QuanLyKTX")
    for row in cursor.fetchall():
        display_text = f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]}"
        listbox.insert(tk.END, display_text)

def chon_sinhvien(event):
    """Khi chọn sinh viên trong Listbox, điền thông tin vào Entry"""
    selection = listbox.get(tk.ACTIVE)
    if not selection:
        return
    data = selection.split('|')
    entry_masv.delete(0, tk.END)
    entry_masv.insert(0, data[0].strip())
    entry_ten.delete(0, tk.END)
    entry_ten.insert(0, data[1].strip())
    entry_phong.delete(0, tk.END)
    entry_phong.insert(0, data[2].strip())
    entry_ngayvao.delete(0, tk.END)
    entry_ngayvao.insert(0, data[3].strip())
    entry_ngayra.delete(0, tk.END)
    entry_ngayra.insert(0, data[4].strip())
    entry_tien.delete(0, tk.END)
    entry_tien.insert(0, data[5].strip())
    entry_trangthai.delete(0, tk.END)
    entry_trangthai.insert(0, data[6].strip())

def them_sinhvien():
    """Thêm sinh viên mới với MaSV kiểu chuỗi tùy ý"""
    try:
        masv = entry_masv.get()
        if not masv:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập MaSV!")
            return

        val = (
            masv,
            entry_ten.get(),
            entry_phong.get(),
            entry_ngayvao.get(),
            entry_ngayra.get() if entry_ngayra.get() != "" else None,
            entry_tien.get(),
            entry_trangthai.get()
        )

        sql = """INSERT INTO QuanLyKTX 
                 (MaSV, HoTen, MaPhong, NgayVao, NgayRa, TienPhong, TrangThai)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        cursor.execute(sql, val)
        conn.commit()
        messagebox.showinfo("Thông báo", "Thêm sinh viên thành công")
        hien_sinhvien()

    except mysql.connector.errors.IntegrityError:
        messagebox.showerror("Lỗi", "MaSV đã tồn tại!")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

def xoa_sinhvien():
    """Xóa sinh viên theo MaSV"""
    try:
        masv = entry_masv.get()
        if not masv:
            messagebox.showwarning("Cảnh báo", "Nhập MaSV cần xóa")
            return

        cursor.execute("DELETE FROM QuanLyKTX WHERE MaSV=%s", (masv,))
        conn.commit()

        messagebox.showinfo("Thông báo", "Xóa sinh viên thành công")
        hien_sinhvien()

    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

def sua_sinhvien():
    """Sửa thông tin sinh viên"""
    try:
        masv = entry_masv.get()
        if not masv:
            messagebox.showwarning("Cảnh báo", "Nhập MaSV cần sửa")
            return

        val = (
            entry_ten.get(),
            entry_phong.get(),
            entry_ngayvao.get(),
            entry_ngayra.get() if entry_ngayra.get() != "" else None,
            entry_tien.get(),
            entry_trangthai.get(),
            masv
        )

        sql = """UPDATE QuanLyKTX SET
                 HoTen=%s, MaPhong=%s, NgayVao=%s, NgayRa=%s, TienPhong=%s, TrangThai=%s
                 WHERE MaSV=%s"""

        cursor.execute(sql, val)
        conn.commit()

        messagebox.showinfo("Thông báo", "Sửa sinh viên thành công")
        hien_sinhvien()

    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


# =================== Giao diện Tkinter ===================
root = tk.Tk()
root.title("Quản lý ký túc xá")
center_window(root, 700, 500)
root.resizable(False, False)
root.configure(bg='black')

# Labels và Entry
labels = ["MaSV", "Họ tên", "Phòng", "Ngày vào (YYYY-MM-DD)", "Ngày ra (YYYY-MM-DD)", "Tiền phòng", "Trạng thái"]
entries = []

for i, text in enumerate(labels):
    tk.Label(root, text=text, bg='black', fg='white').grid(row=i, column=0, padx=5, pady=5, sticky="w")
    entry = tk.Entry(root, bg='black', fg='white', insertbackground='white')
    entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
    entries.append(entry)

entry_masv, entry_ten, entry_phong, entry_ngayvao, entry_ngayra, entry_tien, entry_trangthai = entries

# Buttons
button_bg = 'gray20'
button_fg = 'white'
tk.Button(root, text="Thêm", width=15, command=them_sinhvien, bg=button_bg, fg=button_fg).grid(row=7, column=0, padx=5, pady=5)
tk.Button(root, text="Sửa", width=15, command=sua_sinhvien, bg=button_bg, fg=button_fg).grid(row=7, column=1, padx=5, pady=5)
tk.Button(root, text="Xóa", width=15, command=xoa_sinhvien, bg=button_bg, fg=button_fg).grid(row=8, column=0, padx=5, pady=5)
tk.Button(root, text="Làm mới", width=15, command=hien_sinhvien, bg=button_bg, fg=button_fg).grid(row=8, column=1, padx=5, pady=5)

# Listbox
frame_listbox = tk.Frame(root, bg='black')
frame_listbox.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

scrollbar = tk.Scrollbar(frame_listbox)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(frame_listbox, width=100, bg='black', fg='white', yscrollcommand=scrollbar.set)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox.yview)

# Sự kiện chọn sinh viên
listbox.bind('<<ListboxSelect>>', chon_sinhvien)

# Load dữ liệu
hien_sinhvien()

root.mainloop()
