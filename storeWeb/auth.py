from flask import Blueprint, render_template, request, redirect, session
from database import get_db_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        tenDangNhap = request.form["tenDangNhap"]
        matKhau = request.form["matKhau"]
        email = request.form["email"]
        hoTen = request.form["hoTen"]
        sdt = request.form["sodienThoai"]
        diaChi = request.form["diaChi"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Kiểm tra trùng tên đăng nhập, email, SDT
        cursor.execute("SELECT * FROM NguoiDung WHERE tenDangNhap = %s", (tenDangNhap,))
        if cursor.fetchone():
            return render_template("register.html", error="Tên đăng nhập đã tồn tại!")

        cursor.execute("SELECT * FROM NguoiDung WHERE email = %s", (email,))
        if cursor.fetchone():
            return render_template("register.html", error="Email đã được sử dụng!")

        cursor.execute("SELECT * FROM NguoiDung WHERE sodienThoai = %s", (sdt,))
        if cursor.fetchone():
            return render_template("register.html", error="Số điện thoại đã được sử dụng!")

        cursor.execute("""
            INSERT INTO NguoiDung (tenDangNhap, matKhau, email, hoTen, sodienThoai, diaChi)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (tenDangNhap, matKhau, email, hoTen, sdt, diaChi))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        tenDangNhap = request.form["tenDangNhap"]
        matKhau = request.form["matKhau"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM NguoiDung
            WHERE tenDangNhap = %s AND matKhau = %s
        """, (tenDangNhap, matKhau))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Lưu session
            session['maNguoiDung'] = user[0]
            session['tenDangNhap'] = user[1]
            session['vaiTro'] = user[7]

            # Chuyển hướng theo vai trò
            if user[7] == 'admin':  # hoặc user['vaiTro'] nếu dùng DictCursor
                return redirect("/admin")  # trang dashboard của admin
            else:
                return redirect("/")  # người dùng bình thường về trang chủ
        else:
            return render_template("login.html", error="Sai tên đăng nhập hoặc mật khẩu!")

    return render_template("login.html")

admin_bp = Blueprint("admin", __name__)

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

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
