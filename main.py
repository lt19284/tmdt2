from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import os
import psycopg2


app = Flask(__name__)
app.secret_key = "172.0.0.1"


db_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")
print("database URL:", db_url)
print("SecretKey:", secret_key)

#Tạo kết nối đến database
def create_connect():
    try:
        conn = psycopg2.connect(
        dbname = "tmdt_db_f6sg",
        user = "tmdt_db_f6sg_user",
        password = "vLP9RsiNLx9UdXQiPWPvBwCDuFfTAcfG",
        host = "dpg-ct586h9u0jms73aci1s0-a.oregon-postgres.render.com",
        port = "5432"
    )
        return conn
    except Exception as e:
        print(f"Lỗi Kết Nối: {e}")
        return None

@app.route("/") 
def index():
    return render_template('index.html')
# Đăng ký Tài Khoản
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
            insert_query = "INSERT INTO users (username, Password, Email, PhoneNumber) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (username, hashed_password, email, phonenumber))
            connection.commit()

            flash("Đăng ký thành công!")
            return redirect(url_for('login'))

        except Error as e:
            print(f"Error: {e}")
            flash("Đã xảy ra lỗi trong quá trình đăng ký.")
            return render_template('register.html')

        finally:
            if cursor:
                cursor.close()  # Đóng cursor ở đây
            if connection and connection.is_connected():
                connection.close()  # Đóng kết nối ở đây

    return render_template('register.html')

# Đăng Nhập Người Dùng
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            connection = create_connect()
            if connection is None:
                return render_template('login.html', error_message="Lỗi Kết Nối Cơ Sở Dữ Liệu")

            cursor = connection.cursor()
            query = "SELECT Password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            cursor.close()  # Đóng cursor ngay sau khi đã lấy kết quả

            if result is None:
                return render_template('login.html', error_message="Tên đăng nhập không tồn tại!")
            if check_password_hash(result[0], password):
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

# Log Out Người Dùng
@app.route('/logout')
def logout():
    #Xoá session để đăng xuất ngườI dùng
    session.pop('username', None)
    flash("Đã Đăng Xuất Thành Công!")
    return redirect(url_for('index'))

# Trang giỏ hàng
@app.route('/cart')
def cart():
    return render_template('cart.html')

#Trang Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
