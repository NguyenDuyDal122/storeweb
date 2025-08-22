import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456789",
        database="storedata"
    )

# Tạo kết nối và con trỏ
conn = get_db_connection()
cursor = conn.cursor()

# Danh sách các câu lệnh tạo bảng
tables = []

# 1. Users
tables.append("""
CREATE TABLE IF NOT EXISTS NguoiDung (
    maNguoiDung INT AUTO_INCREMENT PRIMARY KEY,
    tenDangNhap VARCHAR(50) NOT NULL,
    matKhau VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    hoTen VARCHAR(100),
    sodienThoai VARCHAR(20),
    diaChi TEXT,
    vaiTro ENUM('user','admin') DEFAULT 'user',
    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Categories
tables.append("""
CREATE TABLE IF NOT EXISTS DanhMuc (
    maDanhMuc INT AUTO_INCREMENT PRIMARY KEY,
    tenDanhMuc VARCHAR(100) NOT NULL
);
""")

# 3. Products
tables.append("""
CREATE TABLE IF NOT EXISTS SanPham (
    maSanPham INT AUTO_INCREMENT PRIMARY KEY,
    tenSanPham VARCHAR(100) NOT NULL,
    mieuTa TEXT,
    gia DECIMAL(10,2),
    diaChiAnh VARCHAR(255),
    maDanhMuc INT,
    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maDanhMuc) REFERENCES DanhMuc(maDanhMuc)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
""")

# 4. Carts
tables.append("""
CREATE TABLE IF NOT EXISTS GioHang (
    maGioHang INT AUTO_INCREMENT PRIMARY KEY,
    maNguoiDung INT,
    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maNguoiDung) REFERENCES NguoiDung(maNguoiDung)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

# 5. Cart_Items
tables.append("""
CREATE TABLE IF NOT EXISTS ChiTietGioHang (
    maChiTietGioHang INT AUTO_INCREMENT PRIMARY KEY,
    maGioHang INT,
    maSanPham INT,
    soLuong INT,
    FOREIGN KEY (maGioHang) REFERENCES GioHang(maGioHang)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (maSanPham) REFERENCES SanPham(maSanPham)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

# 6. Orders
tables.append("""
CREATE TABLE IF NOT EXISTS DonHang (
    maDonHang INT AUTO_INCREMENT PRIMARY KEY,
    maNguoiDung INT,
    tongGia DECIMAL(10,2),
    diaChiGiaoHang TEXT,
    phuongThucThanhToan ENUM('COD','ZaloPay') DEFAULT 'COD',
    trangThai ENUM('pending','confirmed','shipped','completed','cancelled') DEFAULT 'pending',
    ngaytao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maNguoiDung) REFERENCES NguoiDung(maNguoiDung)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
""")

# 7. Order_Details
tables.append("""
CREATE TABLE IF NOT EXISTS ChiTietDonHang (
    maChiTietDonHang INT AUTO_INCREMENT PRIMARY KEY,
    maDonHang INT,
    maSanPham INT,
    soLuong INT,
    gia DECIMAL(10,2),
    FOREIGN KEY (maDonHang) REFERENCES DonHang(maDonHang)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (maSanPham) REFERENCES SanPham(maSanPham)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

# 8. Reviews
tables.append("""
CREATE TABLE IF NOT EXISTS DanhGia (
    maDanhGia INT AUTO_INCREMENT PRIMARY KEY,
    maNguoiDung INT,
    maSanPham INT,
    maChiTietDonHang INT,
    danhGia INT CHECK (danhGia BETWEEN 1 AND 5),
    binhLuan TEXT,
    phanHoi TEXT,
    ngayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maNguoiDung) REFERENCES NguoiDung(maNguoiDung)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (maSanPham) REFERENCES SanPham(maSanPham)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (maChiTietDonHang) REFERENCES ChiTietDonHang(maChiTietDonHang)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
""")

# Thực thi từng câu lệnh
for sql in tables:
    cursor.execute(sql)

conn.commit()
print("✅ Đã tạo xong 8 bảng trong MySQL.")

# Đóng kết nối
cursor.close()
conn.close()
