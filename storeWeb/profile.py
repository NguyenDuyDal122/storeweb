from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from database import get_db_connection

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/thong-tin-ca-nhan")
def thong_tin_ca_nhan():
    if "maNguoiDung" not in session:
        return redirect(url_for("login"))  # Nếu chưa đăng nhập thì chuyển hướng đến login

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM NguoiDung WHERE maNguoiDung = %s", (session["maNguoiDung"],))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("thong_tin_ca_nhan.html", user=user)


@profile_bp.route("/doi-mat-khau", methods=["GET", "POST"])
def doi_mat_khau():
    if "maNguoiDung" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        matKhauCu = request.form["matKhauCu"]
        matKhauMoi = request.form["matKhauMoi"]
        nhapLai = request.form["nhapLai"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Lấy mật khẩu hiện tại từ DB
        cursor.execute("SELECT matKhau FROM NguoiDung WHERE maNguoiDung = %s", (session["maNguoiDung"],))
        user = cursor.fetchone()

        if not user:
            flash("Người dùng không tồn tại!", "danger")
            return redirect(url_for("profile.doi_mat_khau"))

        # So sánh mật khẩu cũ (ở đây đang để plain text, khuyên bạn nên hash bằng bcrypt)
        if matKhauCu != user["matKhau"]:
            flash("❌ Mật khẩu cũ không chính xác!", "danger")
            return redirect(url_for("profile.doi_mat_khau"))

        if matKhauMoi != nhapLai:
            flash("❌ Mật khẩu mới nhập lại không khớp!", "danger")
            return redirect(url_for("profile.doi_mat_khau"))

        # Cập nhật mật khẩu mới
        cursor.execute("UPDATE NguoiDung SET matKhau = %s WHERE maNguoiDung = %s",
                       (matKhauMoi, session["maNguoiDung"]))
        conn.commit()

        cursor.close()
        conn.close()

        flash("✅ Đổi mật khẩu thành công!", "success")
        return redirect(url_for("profile.thong_tin_ca_nhan"))

    return render_template("doi_mat_khau.html")