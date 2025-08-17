# payment.py
from flask import Blueprint, render_template, request, session, redirect, url_for
from database import get_db_connection

payment_bp = Blueprint("payment_bp", __name__)

@payment_bp.route("/xac-nhan-don-hang", methods=["POST"])
def xac_nhan_don_hang():
    if "tenDangNhap" not in session:
        return redirect("/login")

    dia_chi_giao_hang = request.form.get("diaChiGiaoHang")
    selected_ids = request.form.getlist("selected_items[]")  # ✅ lấy sản phẩm được chọn

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Lấy thông tin người dùng
        cursor.execute("SELECT * FROM NguoiDung WHERE tenDangNhap = %s", (session["tenDangNhap"],))
        user = cursor.fetchone()

        # Lấy giỏ hàng
        cursor.execute("SELECT * FROM GioHang WHERE maNguoiDung = %s", (user["maNguoiDung"],))
        cart = cursor.fetchone()

        if not cart:
            return "Giỏ hàng trống", 400

        # Nếu không chọn sản phẩm nào thì báo lỗi
        if not selected_ids:
            return "Vui lòng chọn sản phẩm để thanh toán", 400

        # Lấy sản phẩm được chọn
        format_strings = ','.join(['%s'] * len(selected_ids))
        cursor.execute(f"""
            SELECT sp.maSanPham, sp.tenSanPham, sp.gia, cth.soLuong
            FROM ChiTietGioHang cth
            JOIN SanPham sp ON cth.maSanPham = sp.maSanPham
            WHERE cth.maGioHang = %s AND sp.maSanPham IN ({format_strings})
        """, [cart["maGioHang"]] + selected_ids)
        items = cursor.fetchall()

        if not items:
            return "Không có sản phẩm hợp lệ để thanh toán", 400

        # Tính tổng tiền (có phí ship 30k)
        tong_gia = sum(float(item["gia"]) * item["soLuong"] for item in items) + 30000

        # Tạo đơn hàng (❌ bỏ phuongThucThanhToan vì bảng không có cột này)
        cursor.execute("""
            INSERT INTO DonHang (maNguoiDung, tongGia, diaChiGiaoHang, trangThai)
            VALUES (%s, %s, %s, %s)
        """, (user["maNguoiDung"], tong_gia, dia_chi_giao_hang, "pending"))
        ma_don_hang = cursor.lastrowid

        # Thêm chi tiết đơn hàng
        for item in items:
            cursor.execute("""
                INSERT INTO ChiTietDonHang (maDonHang, maSanPham, soLuong, gia)
                VALUES (%s, %s, %s, %s)
            """, (ma_don_hang, item["maSanPham"], item["soLuong"], item["gia"]))

        # Xóa các sản phẩm đã đặt khỏi giỏ hàng
        cursor.execute(f"""
            DELETE FROM ChiTietGioHang 
            WHERE maGioHang = %s AND maSanPham IN ({format_strings})
        """, [cart["maGioHang"]] + selected_ids)

        conn.commit()
        return redirect(url_for("payment_bp.hoa_don", ma_don_hang=ma_don_hang))

    except Exception as e:
        conn.rollback()
        return f"Lỗi khi xác nhận đơn hàng: {str(e)}", 500

    finally:
        cursor.close()
        conn.close()

@payment_bp.route("/hoa-don/<int:ma_don_hang>")
def hoa_don(ma_don_hang):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Lấy thông tin đơn hàng
    cursor.execute("""
        SELECT dh.*, nd.hoTen, nd.email, nd.sodienThoai
        FROM DonHang dh
        JOIN NguoiDung nd ON dh.maNguoiDung = nd.maNguoiDung
        WHERE dh.maDonHang = %s
    """, (ma_don_hang,))
    don_hang = cursor.fetchone()

    # Lấy danh sách sản phẩm
    cursor.execute("""
        SELECT sp.tenSanPham, sp.diaChiAnh, ctdh.soLuong, ctdh.gia
        FROM ChiTietDonHang ctdh
        JOIN SanPham sp ON ctdh.maSanPham = sp.maSanPham
        WHERE ctdh.maDonHang = %s
    """, (ma_don_hang,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("hoadon.html", don_hang=don_hang, items=items)


@payment_bp.route("/mua_ngay", methods=["POST"])
def mua_ngay():
    if "tenDangNhap" not in session:
        return redirect("/login")

    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM NguoiDung WHERE tenDangNhap = %s", (session["tenDangNhap"],))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM SanPham WHERE maSanPham = %s", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product:
        return "Sản phẩm không tồn tại", 404

    total_price = float(product["gia"]) * quantity

    return render_template("checkout.html",
                           user=user,
                           items=[{
                               "maSanPham": product["maSanPham"],
                               "tenSanPham": product["tenSanPham"],
                               "diaChiAnh": product["diaChiAnh"],
                               "soLuong": quantity,
                               "gia": product["gia"]
                           }],
                           total_price=total_price,
                           is_mua_ngay=True)


@payment_bp.route("/mua_ngay_thanh_toan", methods=["POST"])
def mua_ngay_thanh_toan():
    if "tenDangNhap" not in session:
        return redirect("/login")

    dia_chi_giao_hang = request.form.get("diaChiGiaoHang")
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM NguoiDung WHERE tenDangNhap = %s", (session["tenDangNhap"],))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM SanPham WHERE maSanPham = %s", (product_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        return "Sản phẩm không tồn tại", 404

    tong_gia = float(product["gia"]) * quantity + 30000  # Thêm phí ship

    cursor.execute("""
        INSERT INTO DonHang (maNguoiDung, tongGia, diaChiGiaoHang, trangThai)
        VALUES (%s, %s, %s, %s)
    """, (user["maNguoiDung"], tong_gia, dia_chi_giao_hang, "pending"))
    conn.commit()
    ma_don_hang = cursor.lastrowid

    cursor.execute("""
        INSERT INTO ChiTietDonHang (maDonHang, maSanPham, soLuong, gia)
        VALUES (%s, %s, %s, %s)
    """, (ma_don_hang, product_id, quantity, product["gia"]))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("payment_bp.hoa_don", ma_don_hang=ma_don_hang))