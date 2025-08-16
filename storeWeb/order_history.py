from flask import Blueprint, session, redirect, render_template
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
