from flask import Flask, render_template, request, session, flash, redirect, url_for, Blueprint
from database import get_db_connection
from auth import auth_bp
from cart import cart_bp
from payment import payment_bp
from order_history import order_history_bp
from review import review_bp
from product_detail import product_detail_bp
from profile import profile_bp
from admin import admin_bp
import cloudinary.api

app = Flask(__name__)
app.secret_key = '123456'

# Đăng ký Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(order_history_bp)
app.register_blueprint(review_bp)
app.register_blueprint(product_detail_bp)
app.register_blueprint(profile_bp)

cloudinary.config(
    cloud_name='dj0oslp3a',
    api_key='393547919889753', # API key
    api_secret='6_mEs6LTpPUCRXuglyGoMy4meg4', # API secret
    secure=True
)

@app.route("/")
def home():
    keyword = request.args.get("keyword", "").strip()
    category_id = request.args.get("category_id")
    page = int(request.args.get("page", 1))
    page_size = 20
    offset = (page - 1) * page_size

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Danh mục
    cursor.execute("SELECT maDanhMuc, tenDanhMuc FROM DanhMuc")
    danhMucList = cursor.fetchall()

    # Truy vấn sản phẩm (có trung bình sao + số đánh giá)
    query = """
        SELECT sp.*, 
               COALESCE(ROUND(AVG(dg.danhGia), 1), 0) AS trungBinhSao,
               COUNT(dg.maDanhGia) AS soDanhGia
        FROM SanPham sp
        LEFT JOIN DanhGia dg ON sp.maSanPham = dg.maSanPham
        WHERE 1=1
    """
    params = []
    if keyword:
        query += " AND sp.tenSanPham LIKE %s"
        params.append(f"%{keyword}%")
    if category_id:
        query += " AND sp.maDanhMuc = %s"
        params.append(category_id)

    query += " GROUP BY sp.maSanPham"

    # Tổng số sản phẩm
    count_query = f"SELECT COUNT(*) AS total FROM ({query}) AS sub"
    cursor.execute(count_query, tuple(params))
    total_products = cursor.fetchone()["total"]
    total_pages = (total_products + page_size - 1) // page_size

    # Lấy sản phẩm phân trang
    query += " LIMIT %s OFFSET %s"
    params.extend([page_size, offset])
    cursor.execute(query, tuple(params))
    sanPhamList = cursor.fetchall()

    # 🆕 Lấy sản phẩm bán chạy (chỉ lấy đơn hàng đã hoàn tất)
    cursor.execute("""
        SELECT sp.*, 
               COALESCE(ROUND(AVG(dg.danhGia), 1), 0) AS trungBinhSao,
               COUNT(dg.maDanhGia) AS soDanhGia,
               SUM(ct.soLuong) AS tongBan
        FROM ChiTietDonHang ct
        JOIN DonHang dh ON ct.maDonHang = dh.maDonHang
        JOIN SanPham sp ON ct.maSanPham = sp.maSanPham
        LEFT JOIN DanhGia dg ON sp.maSanPham = dg.maSanPham
        WHERE dh.trangThai = 'completed'
        GROUP BY sp.maSanPham
        HAVING tongBan >= 20
        ORDER BY tongBan DESC
        LIMIT 10
    """)
    best_sellers = cursor.fetchall()

    # Thông tin người dùng
    tenDangNhap = session.get("tenDangNhap")
    hoTen = None
    if tenDangNhap:
        cursor.execute("SELECT hoTen FROM NguoiDung WHERE tenDangNhap = %s", (tenDangNhap,))
        user = cursor.fetchone()
        if user:
            hoTen = user["hoTen"]

    cursor.close()
    conn.close()

    return render_template(
        "home.html",
        tenDangNhap=tenDangNhap,
        hoTen=hoTen,
        vaiTro=session.get("vaiTro"),
        sanPhamList=sanPhamList,
        danhMucList=danhMucList,
        keyword=keyword,
        category_id=category_id,
        current_page=page,
        total_pages=total_pages,
        best_sellers=best_sellers  # 🆕 Truyền ra template
    )

@app.context_processor
def inject_user():
    tenDangNhap = session.get("tenDangNhap")
    hoTen = None
    if tenDangNhap:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT hoTen FROM NguoiDung WHERE tenDangNhap = %s", (tenDangNhap,))
        user = cursor.fetchone()
        if user:
            hoTen = user["hoTen"]
        cursor.close()
        conn.close()

    return dict(
        tenDangNhap=tenDangNhap,
        vaiTro=session.get("vaiTro"),
        maNguoiDung=session.get("maNguoiDung"),
        hoTen=hoTen
    )

if __name__ == "__main__":
    app.run(debug=True)