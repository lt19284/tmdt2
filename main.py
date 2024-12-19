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
    username = session.get('username')
    return render_template('index.html', username=username)

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
            connection = create_connect()
            if connection is None:
                return render_template('login.html', error_message="Lỗi Kết Nối Cơ Sở Dữ Liệu")

            cursor = connection.cursor()
            query = "SELECT password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result is None:
                return render_template('login.html', error_message="Tên đăng nhập không tồn tại!")
            if check_password_hash(result[0], password):
                session['username'] = username  # Lưu thông tin người dùng vào session
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
    session.pop('username', None)  # Xóa thông tin người dùng trong session
    flash("Đã Đăng Xuất Thành Công!")
    return redirect(url_for('index'))  # Quay về trang chủ


# Kiểm tra xem người dùng đã đăng nhập chưa
def is_logged_in():
    return 'user_id' in session

# Trang giỏ hàng (chỉ cho phép truy cập khi đăng nhập)
@app.route('/cart')
def cart():
    # Kiểm tra xem người dùng đã đăng nhập hay chưa bằng cách kiểm tra session
    if not session.get('username'):  # Kiểm tra nếu không có 'username' trong session
        flash("Bạn phải đăng nhập để truy cập giỏ hàng!")
        return redirect(url_for('login'))  # Chuyển hướng đến trang đăng nhập nếu chưa đăng nhập
    # Nếu đã đăng nhập, hiển thị trang giỏ hàng
    return render_template('cart.html')


    # Lấy danh sách sản phẩm trong giỏ hàng của người dùng
    user_id = session['user_id']
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name, p.price, c.quantity 
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        """, (user_id,))
        cart_items = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('cart.html', cart_items=cart_items)

# Trang contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add-to-cart')
def add_to_cart():
    return render_template('add-to-cart.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
