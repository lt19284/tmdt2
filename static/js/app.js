function addToCart(productId, quantity = 1) {
    // Gửi yêu cầu POST tới server
    fetch('/cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to add product to cart');
        }
        return response.json();
    })
    .then(data => {
        alert(data.message || 'Sản phẩm đã được thêm vào giỏ hàng!');
        // Cập nhật giao diện nếu cần
    })
    .catch(error => {
        console.error('Error adding product to cart:', error);
        alert('Đã xảy ra lỗi khi thêm sản phẩm vào giỏ hàng.');
    });
}

// Gắn sự kiện cho các nút "Thêm vào giỏ hàng"
document.addEventListener('DOMContentLoaded', () => {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.dataset.productId;
            const quantity = button.dataset.quantity || 1; // Lấy số lượng mặc định là 1
            addToCart(productId, quantity);
        });
    });
});
