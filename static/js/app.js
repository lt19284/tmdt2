
document.addEventListener('DOMContentLoaded', () => {
    // Lắng nghe sự kiện thêm vào giỏ hàng
    const addToCartButtons = document.querySelectorAll('.add-to-cart');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault();

            // Lấy thông tin sản phẩm từ thuộc tính data-*
            const productId = button.getAttribute('data-product-id');
            const productName = button.getAttribute('data-product-name');
            const productPrice = button.getAttribute('data-product-price');
            const productQuantity = 1; // Mặc định số lượng là 1

            // Dữ liệu sản phẩm
            const productData = {
                id: productId,
                name: productName,
                price: productPrice,
                quantity: productQuantity
            };

            // Gửi yêu cầu tới server bằng Fetch API
            fetch('/cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(productData)
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Không thể thêm vào giỏ hàng!');
                }
            })
            .then(data => {
                // Hiển thị thông báo thành công
                alert(data.message || 'Đã thêm vào giỏ hàng!');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Có lỗi xảy ra khi thêm vào giỏ hàng!');
            });
        });
    });
});
