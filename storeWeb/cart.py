from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database import get_db_connection

cart_bp = Blueprint("cart_bp", __name__)

@cart_bp.route("/them_gio_hang", methods=["POST"])
def them_gio_hang():
    if "tenDangNhap" not in session:
        flash("Bạn cần đăng nhập trước khi thêm giỏ hàng!", "warning")
        return redirect(url_for("auth.login"))

    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT maNguoiDung FROM NguoiDung WHERE tenDangNhap=%s", (session['tenDangNhap'],))
    user = cursor.fetchone()
    if not user:
        flash("Không tìm thấy thông tin người dùng!", "danger")
        return redirect(url_for("home"))
    maNguoiDung = user['maNguoiDung']

    cursor.execute("SELECT maGioHang FROM GioHang WHERE maNguoiDung=%s", (maNguoiDung,))
    gio_hang = cursor.fetchone()
    if not gio_hang:
        cursor.execute("INSERT INTO GioHang (maNguoiDung) VALUES (%s)", (maNguoiDung,))
        conn.commit()
        maGioHang = cursor.lastrowid
    else:
        maGioHang = gio_hang['maGioHang']

    cursor.execute("""
        SELECT soLuong FROM ChiTietGioHang 
        WHERE maGioHang=%s AND maSanPham=%s
    """, (maGioHang, product_id))
    item = cursor.fetchone()

    if item:
        cursor.execute("""
            UPDATE ChiTietGioHang 
            SET soLuong = soLuong + %s
            WHERE maGioHang=%s AND maSanPham=%s
        """, (quantity, maGioHang, product_id))
    else:
        cursor.execute("""
            INSERT INTO ChiTietGioHang (maGioHang, maSanPham, soLuong)
            VALUES (%s, %s, %s)
        """, (maGioHang, product_id, quantity))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("home"))


@cart_bp.route("/giohang")
def cart():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cart_items = []
    total_price = 0

    if "tenDangNhap" in session:
        cursor.execute("""
            SELECT gh.maGioHang
            FROM GioHang gh
            JOIN NguoiDung nd ON gh.maNguoiDung = nd.maNguoiDung
            WHERE nd.tenDangNhap = %s
        """, (session["tenDangNhap"],))
        cart = cursor.fetchone()

        if cart:
            cursor.execute("""
                SELECT sp.maSanPham, sp.tenSanPham, sp.gia, sp.diaChiAnh, cth.soLuong
                FROM ChiTietGioHang cth
                JOIN SanPham sp ON cth.maSanPham = sp.maSanPham
                WHERE cth.maGioHang = %s
            """, (cart["maGioHang"],))
            cart_items = cursor.fetchall()
    else:
        cart_items = session.get("cart", [])

    total_price = sum(float(item["gia"]) * int(item["soLuong"]) for item in cart_items)

    cursor.close()
    conn.close()
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)


@cart_bp.route("/thanhtoan-giohang", methods=["POST"])
def checkout():
    # Kiểm tra đăng nhập
    if "tenDangNhap" not in session:
        flash("Vui lòng đăng nhập để thanh toán!", "warning")
        return redirect(url_for("auth_bp.login"))

    # Lấy danh sách sản phẩm được chọn
    selected_ids = request.form.getlist("selected_items[]")
    if not selected_ids:
        flash("Vui lòng chọn ít nhất 1 sản phẩm để thanh toán!", "warning")
        return redirect(url_for("cart_bp.cart"))

    # Ép kiểu int (nếu cần)
    try:
        selected_ids = [int(x) for x in selected_ids]
    except ValueError:
        flash("Danh sách sản phẩm không hợp lệ!", "danger")
        return redirect(url_for("cart_bp.cart"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Lấy thông tin người dùng
    cursor.execute("""
        SELECT maNguoiDung, hoTen, email, soDienThoai, diaChi
        FROM NguoiDung
        WHERE tenDangNhap = %s
    """, (session["tenDangNhap"],))
    user_info = cursor.fetchone()
    if not user_info:
        flash("Không tìm thấy thông tin người dùng!", "danger")
        return redirect(url_for("cart_bp.cart"))

    # Lấy sản phẩm trong giỏ hàng
    format_strings = ','.join(['%s'] * len(selected_ids))
    cursor.execute(f"""
        SELECT sp.maSanPham, sp.tenSanPham, sp.gia, cth.soLuong, sp.diaChiAnh
        FROM ChiTietGioHang cth
        JOIN SanPham sp ON cth.maSanPham = sp.maSanPham
        JOIN GioHang gh ON cth.maGioHang = gh.maGioHang
        JOIN NguoiDung nd ON gh.maNguoiDung = nd.maNguoiDung
        WHERE nd.tenDangNhap = %s AND sp.maSanPham IN ({format_strings})
    """, [session["tenDangNhap"]] + selected_ids)

    items_to_pay = cursor.fetchall()

    # Tính tổng tiền
    total_price = sum(float(item["gia"]) * int(item["soLuong"]) for item in items_to_pay)

    cursor.close()
    conn.close()

    return render_template("checkout.html", user=user_info, items=items_to_pay, total_price=total_price)


@cart_bp.route("/xoa-gio-hang", methods=["POST"])
def remove_from_cart():
    ma_san_pham = request.form.get("product_id")

    if "tenDangNhap" not in session:
        flash("Bạn cần đăng nhập để xóa sản phẩm", "warning")
        return redirect(url_for("cart_bp.cart"))

    if not ma_san_pham:
        flash("Không tìm thấy sản phẩm để xóa", "warning")
        return redirect(url_for("cart_bp.cart"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE c
            FROM ChiTietGioHang c
            JOIN GioHang g ON c.maGioHang = g.maGioHang
            JOIN NguoiDung nd ON g.maNguoiDung = nd.maNguoiDung
            WHERE nd.tenDangNhap = %s AND c.maSanPham = %s
        """, (session["tenDangNhap"], ma_san_pham))
        conn.commit()
        flash("Sản phẩm đã được xóa khỏi giỏ hàng", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Lỗi khi xóa sản phẩm: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("cart_bp.cart"))