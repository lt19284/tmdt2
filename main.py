from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
import os
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "172.0.0.1"

# Cấu hình kết nối cơ sở dữ liệu
def create_connect():
    try:
        conn = psycopg2.connect(
            dbname="tmdt_db_f6sg",
            user="tmdt_db_f6sg_user",
            password="vLP9RsiNLx9UdXQiPWPvBwCDuFfTAcfG",
            host="dpg-ct586h9u0jms73aci1s0-a.oregon-postgres.render.com",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Lỗi Kết Nối: {e}")
        return None

# Trang chính
@app.route("/")
def index():
    return render_template('index.html')

# Đăng ký tài khoản
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')

        # Kiểm tra mật khẩu
        if password != confirm_password:
            return render_template('register.html', error_message="Mật khẩu không khớp, vui lòng thử lại!")

        # Mã hóa mật khẩu trước khi lưu
        hashed_password = generate_password_hash(password)

        try:
            connection = create_connect()
            if connection is None:
                return render_template('register.html', error_message="Lỗi kết nối cơ sở dữ liệu!")

            cursor = connection.cursor()
            insert_query = "INSERT INTO users (username, password, email, phonenumber) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, hashed_password, email, phonenumber))
            connection.commit()

            flash("Đăng ký thành công!")
            return redirect(url_for('login'))

        except psycopg2.Error as e:
            print(f"Error: {e}")
            flash(f"Đã xảy ra lỗi trong quá trình đăng ký: {e}")
            return render_template('register.html')

        finally:
            if cursor:
                cursor.close()
            if connection and connection.closed == 0:
                connection.close()

    return render_template('register.html')

# Đăng nhập người dùng
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            # Kết nối cơ sở dữ liệu
            connection = create_connect()
            if connection is None:
                return render_template('login.html', error_message="Lỗi Kết Nối Cơ Sở Dữ Liệu")

            cursor = connection.cursor()
            query = "SELECT password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            # Kiểm tra nếu không có kết quả trả về từ truy vấn
            if result is None:
                return render_template('login.html', error_message="Tên đăng nhập không tồn tại!")

            password_hash = result[0]  # Lấy mật khẩu đã băm từ cơ sở dữ liệu

            # Kiểm tra nếu mật khẩu là None (có thể bị lỗi trong cơ sở dữ liệu)
            if password_hash is None:
                return render_template('login.html', error_message="Lỗi: Không có mật khẩu được lưu trữ cho người dùng này.")

            # Kiểm tra mật khẩu đã băm với mật khẩu người dùng nhập vào
            if check_password_hash(password_hash, password):
                session['username'] = username
                flash("Đăng Nhập Thành Công!")
                return redirect(url_for('index'))  # Chuyển đến trang chính khi đăng nhập thành công
            else:
                return render_template('login.html', error_message="Mật khẩu không đúng!")

        except Error as e:
            print(f"Error: {e}")
            flash("Đã xảy ra lỗi trong quá trình đăng nhập.")
            return render_template('login.html')

        finally:
            if connection:
                connection.close()  # Đóng kết nối ở đây
    return render_template('login.html')

# Đăng xuất người dùng
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Đã Đăng Xuất Thành Công!")
    return redirect(url_for('index'))

# Trang giỏ hàng
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Trang contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
