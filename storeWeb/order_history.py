from flask import Blueprint, session, redirect, render_template, flash, url_for
from database import get_db_connection

order_history_bp = Blueprint('order_history', __name__)

@order_history_bp.route('/lich-su-don-hang')
def lich_su_don_hang():
    if 'maNguoiDung' not in session:
        return redirect('/login')

    maNguoiDung = session['maNguoiDung']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM DonHang
        WHERE maNguoiDung = %s
        ORDER BY ngayTao DESC
    """, (maNguoiDung,))
    don_hangs = cursor.fetchall()

    for don_hang in don_hangs:
        cursor.execute("""
            SELECT cth.maChiTietDonHang,
                   cth.maSanPham, 
                   sp.tenSanPham, 
                   cth.soLuong, 
                   cth.gia,
                   (SELECT COUNT(*) FROM DanhGia dg 
                    WHERE dg.maNguoiDung = %s 
                      AND dg.maChiTietDonHang = cth.maChiTietDonHang) AS daDanhGia
            FROM ChiTietDonHang cth
            JOIN SanPham sp ON cth.maSanPham = sp.maSanPham
            WHERE cth.maDonHang = %s
        """, (maNguoiDung, don_hang['maDonHang']))
        don_hang['chi_tiet'] = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("lich_su_don_hang.html", don_hangs=don_hangs)

@order_history_bp.route("/huy-don-hang/<int:maDonHang>", methods=["POST"])
def huy_don_hang(maDonHang):
    if 'maNguoiDung' not in session:
        return redirect('/login')

    maNguoiDung = session['maNguoiDung']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Chỉ cho phép hủy nếu đơn hàng thuộc user và trạng thái = pending
        cursor.execute("""
            UPDATE DonHang
            SET trangThai = 'cancelled'
            WHERE maDonHang = %s AND maNguoiDung = %s AND trangThai = 'pending'
        """, (maDonHang, maNguoiDung))
        conn.commit()

        if cursor.rowcount > 0:
            flash("🛑 Đơn hàng đã được hủy thành công!", "success")
        else:
            flash("⚠ Không thể hủy đơn hàng này (có thể đã được xử lý).", "warning")

    except Exception as e:
        conn.rollback()
        flash(f"❌ Lỗi khi hủy đơn hàng: {e}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("order_history.lich_su_don_hang"))
