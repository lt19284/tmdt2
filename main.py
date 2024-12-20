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
        print(f"Lỗi kết nối: {e}")
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

        if password != confirm_password:
            return render_template('register.html', error_message="Mật khẩu không khớp!")

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
            print(f"Lỗi: {e}")
            flash("Đã xảy ra lỗi trong quá trình đăng ký.")
            return render_template('register.html')
        finally:
            if cursor:
                cursor.close()
            if connection and connection.closed == 0:
                connection.close()

    return render_template('register.html')

# Đăng nhập
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            connection = create_connect()
            if connection is None:
                return render_template('login.html', error_message="Lỗi kết nối cơ sở dữ liệu!")

            cursor = connection.cursor()
            query = "SELECT password FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result is None:
                return render_template('login.html', error_message="Tên đăng nhập không tồn tại!")
            if check_password_hash(result[0], password):
                session['username'] = username
                flash("Đăng nhập thành công!")
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error_message="Mật khẩu không đúng!")
        except psycopg2.Error as e:
            print(f"Lỗi: {e}")
            flash("Đã xảy ra lỗi trong quá trình đăng nhập.")
            return render_template('login.html')
        finally:
            if connection:
                connection.close()

    return render_template('login.html')

# Đăng xuất
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Đăng xuất thành công!")
    return redirect(url_for('index'))

# Trang giỏ hàng
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        data = request.json
        product_id = data.get('id')
        name = data.get('name')
        price = float(data.get('price'))
        quantity = int(data.get('quantity'))

        if 'cart_items' not in session:
            session['cart_items'] = []

        for item in session['cart_items']:
            if item['id'] == product_id:
                item['quantity'] += quantity
                session.modified = True
                return jsonify({'message': 'Sản phẩm đã được cập nhật trong giỏ hàng!'})

        session['cart_items'].append({
            'id': product_id,
            'name': name,
            'price': price,
            'quantity': quantity
        })
        session.modified = True
        return jsonify({'message': 'Sản phẩm đã được thêm vào giỏ hàng!'})

    cart_items = session.get('cart_items', [])
    return render_template('cart.html', cart_items=cart_items)

# Xóa sản phẩm khỏi giỏ hàng
@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    if request.method == 'POST':
        data = request.json
        product_id = data.get('id')

        if 'cart_items' in session:
            session['cart_items'] = [item for item in session['cart_items'] if item['id'] != product_id]
            session.modified = True
            return jsonify({'message': 'Sản phẩm đã được xóa khỏi giỏ hàng!'})

        return jsonify({'message': 'Không tìm thấy sản phẩm trong giỏ hàng!'})

# Tìm kiếm sản phẩm
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    results = []  # Kết quả giả lập, thay bằng dữ liệu thực từ database
    return render_template('search.html', query=query, results=results)

# Thanh toán
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        flash('Thanh toán thành công!')
        session.pop('cart_items', None)  # Xóa giỏ hàng sau khi thanh toán
        return redirect(url_for('index'))
    cart_items = session.get('cart_items', [])
    return render_template('checkout.html', cart_items=cart_items)

# Thêm sản phẩm
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' not in session:
        flash("Bạn phải đăng nhập để thêm sản phẩm!", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')

        if not name or not price:
            flash("Tên sản phẩm và giá không được để trống!", "danger")
            return redirect(url_for('add_product'))

        try:
            connection = create_connect()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO products (name, price, description) VALUES (%s, %s, %s)",
                (name, price, description)
            )
            connection.commit()
            flash("Sản phẩm đã được thêm thành công!", "success")
        except Exception as e:
            flash(f"Lỗi khi thêm sản phẩm: {e}", "danger")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return redirect(url_for('index'))

    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
