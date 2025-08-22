from flask import Blueprint, render_template
from database import get_db_connection

product_detail_bp = Blueprint('product_detail', __name__)

@product_detail_bp.route("/product/<int:maSanPham>")
def product_detail(maSanPham):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT sp.*, dm.tenDanhMuc
        FROM SanPham sp
        LEFT JOIN DanhMuc dm ON sp.maDanhMuc = dm.maDanhMuc
        WHERE sp.maSanPham = %s
    """, (maSanPham,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        return "Sản phẩm không tồn tại", 404

    cursor.execute("""
        SELECT dg.*, nd.hoTen
        FROM DanhGia dg
        JOIN NguoiDung nd ON dg.maNguoiDung = nd.maNguoiDung
        WHERE dg.maSanPham = %s
        ORDER BY dg.ngayTao DESC
    """, (maSanPham,))
    reviews = cursor.fetchall()
    avg_rating = sum(rv['danhGia'] for rv in reviews) / len(reviews) if reviews else None

    cursor.close()
    conn.close()

    return render_template(
        "product_detail.html",
        product=product,
        reviews=reviews,
        avg_rating=avg_rating
    )
