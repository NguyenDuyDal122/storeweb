import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from database import get_db_connection

admin_bp = Blueprint("admin", __name__, template_folder="templates")

# Kiểm tra quyền admin trước mỗi request
@admin_bp.before_request
def check_admin():
    if 'vaiTro' not in session or session['vaiTro'] != 'admin':
        return redirect("/login")

# Dashboard admin
@admin_bp.route("/admin")
def dashboard():
    # Thông tin tạm thời
    doanh_thu = 1500000
    tong_don = 15
    tong_mon = 4
    tong_user = 2
    return render_template("admin_dashboard.html",
                           doanh_thu=doanh_thu,
                           tong_don=tong_don,
                           tong_mon=tong_mon,
                           tong_user=tong_user)

# Danh sách user
@admin_bp.route("/admin/nguoidung")
def manage_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM NguoiDung")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("manage_users.html", users=users)

# Thêm user
@admin_bp.route("/admin/nguoidung/them", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        tenDangNhap = request.form["tenDangNhap"]
        matKhau = request.form["matKhau"]
        hoTen = request.form["hoTen"]
        email = request.form["email"]
        sodienThoai = request.form["sodienThoai"]
        diaChi = request.form["diaChi"]
        vaiTro = request.form.get("vaiTro", "user")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NguoiDung (tenDangNhap, matKhau, hoTen, email, sodienThoai, diaChi, vaiTro)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (tenDangNhap, matKhau, hoTen, email, sodienThoai, diaChi, vaiTro))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Thêm tài khoản thành công!")
        return redirect(url_for("admin.manage_users"))
    return render_template("add_edit_user.html", user=None)

# Sửa user
@admin_bp.route("/admin/nguoidung/sua/<int:user_id>", methods=["GET","POST"])
def edit_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        hoTen = request.form["hoTen"]
        email = request.form["email"]
        sodienThoai = request.form["sodienThoai"]
        diaChi = request.form["diaChi"]
        vaiTro = request.form.get("vaiTro", "user")
        cursor.execute("""
            UPDATE NguoiDung
            SET hoTen=%s,email=%s,sodienThoai=%s,diaChi=%s,vaiTro=%s
            WHERE maNguoiDung=%s
        """, (hoTen,email,sodienThoai,diaChi,vaiTro,user_id))
        conn.commit()
        flash("Cập nhật tài khoản thành công!")
        cursor.close()
        conn.close()
        return redirect(url_for("admin.manage_users"))
    # GET: lấy thông tin user
    cursor.execute("SELECT * FROM NguoiDung WHERE maNguoiDung=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("add_edit_user.html", user=user)

# Xóa user
@admin_bp.route("/admin/nguoidung/xoa/<int:user_id>")
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM NguoiDung WHERE maNguoiDung=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Xóa tài khoản thành công!")
    return redirect(url_for("admin.manage_users"))

# ----------------------
# Quản lý danh mục món ăn
# ----------------------

# Danh sách danh mục
@admin_bp.route("/admin/danhmuc")
def manage_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM DanhMuc ORDER BY maDanhMuc DESC")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("manage_categories.html", categories=categories)

# Thêm danh mục
@admin_bp.route("/admin/danhmuc/them", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        tenDanhMuc = request.form["tenDanhMuc"].strip()
        if not tenDanhMuc:
            flash("Tên danh mục không được để trống!")
            return redirect(url_for("admin.add_category"))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO DanhMuc (tenDanhMuc) VALUES (%s)", (tenDanhMuc,))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Thêm danh mục thành công!")
        return redirect(url_for("admin.manage_categories"))
    return render_template("add_edit_category.html", category=None)

# Sửa danh mục
@admin_bp.route("/admin/danhmuc/sua/<int:category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        tenDanhMuc = request.form["tenDanhMuc"].strip()
        if not tenDanhMuc:
            flash("Tên danh mục không được để trống!")
            return redirect(url_for("admin.edit_category", category_id=category_id))
        cursor.execute("UPDATE DanhMuc SET tenDanhMuc=%s WHERE maDanhMuc=%s", (tenDanhMuc, category_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Cập nhật danh mục thành công!")
        return redirect(url_for("admin.manage_categories"))
    # GET: lấy thông tin danh mục
    cursor.execute("SELECT * FROM DanhMuc WHERE maDanhMuc=%s", (category_id,))
    category = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("add_edit_category.html", category=category)

# Xóa danh mục
@admin_bp.route("/admin/danhmuc/xoa/<int:category_id>")
def delete_category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM DanhMuc WHERE maDanhMuc=%s", (category_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Xóa danh mục thành công!")
    return redirect(url_for("admin.manage_categories"))

# ----------------------
# Quản lý món ăn vặt
# ----------------------

# Danh sách món ăn
@admin_bp.route("/admin/monan")
def manage_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT sp.*, dm.tenDanhMuc 
        FROM SanPham sp
        LEFT JOIN DanhMuc dm ON sp.maDanhMuc = dm.maDanhMuc
        ORDER BY sp.maSanPham DESC
    """)
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("manage_products.html", products=products)

# Thêm món ăn
@admin_bp.route("/admin/monan/them", methods=["GET", "POST"])
def add_product():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM DanhMuc")
    categories = cursor.fetchall()  # để chọn danh mục
    if request.method == "POST":
        tenSanPham = request.form["tenSanPham"].strip()
        mieuTa = request.form.get("mieuTa", "")
        gia = request.form.get("gia", 0)
        maDanhMuc = request.form.get("maDanhMuc")

        # 🆕 Upload ảnh lên Cloudinary
        file = request.files.get("anh")
        diaChiAnh = None
        if file:
            upload_result = cloudinary.uploader.upload(file)
            diaChiAnh = upload_result.get("secure_url")

        cursor.execute("""
            INSERT INTO SanPham (tenSanPham, mieuTa, gia, diaChiAnh, maDanhMuc)
            VALUES (%s, %s, %s, %s, %s)
        """, (tenSanPham, mieuTa, gia, diaChiAnh, maDanhMuc))
        conn.commit()
        flash("Thêm món ăn thành công!")
        cursor.close()
        conn.close()
        return redirect(url_for("admin.manage_products"))

    cursor.close()
    conn.close()
    return render_template("add_edit_product.html", product=None, categories=categories)

# Sửa món ăn
@admin_bp.route("/admin/monan/sua/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM SanPham WHERE maSanPham=%s", (product_id,))
    product = cursor.fetchone()

    cursor.execute("SELECT * FROM DanhMuc")
    categories = cursor.fetchall()

    if request.method == "POST":
        tenSanPham = request.form["tenSanPham"].strip()
        mieuTa = request.form.get("mieuTa", "")
        gia = request.form.get("gia", 0)
        maDanhMuc = request.form.get("maDanhMuc")

        # 🆕 Nếu có upload ảnh mới thì thay ảnh, còn không thì giữ ảnh cũ
        file = request.files.get("anh")
        diaChiAnh = product["diaChiAnh"]  # giữ ảnh cũ
        if file:
            upload_result = cloudinary.uploader.upload(file)
            diaChiAnh = upload_result.get("secure_url")

        cursor.execute("""
            UPDATE SanPham
            SET tenSanPham=%s, mieuTa=%s, gia=%s, diaChiAnh=%s, maDanhMuc=%s
            WHERE maSanPham=%s
        """, (tenSanPham, mieuTa, gia, diaChiAnh, maDanhMuc, product_id))
        conn.commit()
        flash("Cập nhật món ăn thành công!")
        cursor.close()
        conn.close()
        return redirect(url_for("admin.manage_products"))

    cursor.close()
    conn.close()
    return render_template("add_edit_product.html", product=product, categories=categories)

# Xóa món ăn
@admin_bp.route("/admin/monan/xoa/<int:product_id>")
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM SanPham WHERE maSanPham=%s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Xóa món ăn thành công!")
    return redirect(url_for("admin.manage_products"))
