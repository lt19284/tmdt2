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
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        data = request.json
        product_id = data.get('id')
        name = data.get('name')
        price = data.get('price')
        quantity = data.get('quantity')

        # Giả lập lưu trữ sản phẩm trong session
        if 'cart_items' not in session:
            session['cart_items'] = []
        session['cart_items'].append({
            'id': product_id,
            'name': name,
            'price': price,
            'quantity': quantity
        })
        session.modified = True

        return jsonify({'message': 'Sản phẩm đã được thêm vào giỏ hàng!'})

    # Lấy danh sách sản phẩm trong giỏ hàng từ session
    cart_items = session.get('cart_items', [])
    return render_template('cart.html', cart_items=cart_items)

# Trang chi tiết sản phẩm
@app.route('/product-detail/<int:product_id>')
def product_detail(product_id):
    # Lấy thông tin chi tiết sản phẩm từ database dựa trên product_id
    product = {}  # Thay bằng truy vấn từ database
    return render_template('product_detail.html', product=product)

# Tìm kiếm sản phẩm
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # Thực hiện tìm kiếm sản phẩm trong database dựa trên query
    results = []  # Thay bằng kết quả tìm kiếm từ database
    return render_template('search.html', query=query, results=results)

# Trang thanh toán
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Xử lý đơn hàng: lưu thông tin vào database, gửi email, v.v.
        flash('Thanh toán thành công!')
        return redirect(url_for('index'))
    # Lấy thông tin giỏ hàng và hiển thị trên trang thanh toán
    cart_items = session.get('cart_items', [])
    return render_template('checkout.html', cart_items=cart_items)
    
#thêm Sản Phẩm
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    # Kiểm tra nếu người dùng chưa đăng nhập
    if 'username' not in session:
        flash("Bạn phải đăng nhập để thêm sản phẩm!", "danger")
        return redirect(url_for('login'))  # Chuyển hướng đến trang đăng nhập

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')

        # Kiểm tra dữ liệu hợp lệ
        if not name or not price:
            flash("Tên sản phẩm và giá không được để trống!", "danger")
            return redirect(url_for('add_product'))

        # Thêm sản phẩm vào cơ sở dữ liệu
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO products (name, price, description) VALUES (%s, %s, %s)",
                (name, price, description)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Sản phẩm đã được thêm thành công!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Có lỗi xảy ra khi thêm sản phẩm: {e}", "danger")
            return redirect(url_for('add_product'))

    # Hiển thị form thêm sản phẩm
    return render_template('add_product.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
