from flask import Blueprint, session, redirect, request, flash
from database import get_db_connection

review_bp = Blueprint('review', __name__)

@review_bp.route('/danh-gia', methods=['POST'])
def danh_gia():
    if 'maNguoiDung' not in session:
        return redirect('/login')

    maNguoiDung = session['maNguoiDung']
    maSanPham = request.form['maSanPham']
    maChiTietDonHang = request.form['maChiTietDonHang']
    danhGia = request.form['danhGia']
    binhLuan = request.form['binhLuan']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT maDanhGia FROM DanhGia
        WHERE maNguoiDung = %s AND maChiTietDonHang = %s
    """, (maNguoiDung, maChiTietDonHang))
    if cursor.fetchone():
        flash("❌ Bạn đã đánh giá sản phẩm này trong đơn hàng này rồi!", "danger")
        cursor.close()
        conn.close()
        return redirect('/lich-su-don-hang')

    cursor.execute("""
        INSERT INTO DanhGia (maNguoiDung, maSanPham, maChiTietDonHang, danhGia, binhLuan)
        VALUES (%s, %s, %s, %s, %s)
    """, (maNguoiDung, maSanPham, maChiTietDonHang, danhGia, binhLuan))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/lich-su-don-hang')
