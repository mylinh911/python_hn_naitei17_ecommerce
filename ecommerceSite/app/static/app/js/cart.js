var updateBtns = document.getElementsByClassName('update-cart');
var removeBtn = document.getElementById('removeBtn');
var checkoutBtn = document.getElementById('checkoutBtn');
var checkboxes = document.getElementsByClassName('product-checkbox');

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productId', productId, 'action', action);
        updateUserOrder(productId, action);
    });
}

removeBtn.addEventListener('click', function() {
    var selectedItems = getSelectedItems();
    var action = 'delete';
    for (var i = 0; i < selectedItems.length; i++) {
        var productId = selectedItems[i].product;
        console.log('productId', selectedItems[i], 'action', action);
        updateUserOrder(productId, action);
    }
});

checkoutBtn.addEventListener('click', function() {
    var orderProductList = [];
    var orderQuantityList = [];
    var selectedItems = getSelectedItems();

    for (var i = 0; i < selectedItems.length; i++) {
        var quantity = selectedItems[i].quantity;
        var product = selectedItems[i].product;
        orderProductList.push(product);
        orderQuantityList.push(quantity);
    }

    checkoutDemo(orderProductList,orderQuantityList);
});

function checkoutDemo(orderProductList,orderQuantityList){
    var url = '/checkout_demo/'
    fetch(url,{
        method: 'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'orderProductList':orderProductList, 'orderQuantityList':orderQuantityList})
    })
    .then((response) => {
        return response.json()
    })
    .then((data) => {
        console.log('data',data)

    })

}

function updateUserOrder(productId, action) {
    console.log('user logged in, success add');
    var url = '/update_item/';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log('data', data);
        if (data.status === 'success') {
            if (action === 'add') {
                var quantityToAdd = prompt('Nhập số lượng sản phẩm:');
                if (quantityToAdd !== null) {
                    quantityToAdd = parseInt(quantityToAdd);

                    if (!isNaN(quantityToAdd) && quantityToAdd > 0) {
                        var url = '/update_item/';
                        var data = {
                            'productId': productId,
                            'action': action,
                            'quantity': quantityToAdd
                        };

                        fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken,
                            },
                            body: JSON.stringify(data)
                        })
                        .then((response) => {
                            return response.json();
                        })
                        .then((data) => {
                            console.log('data', data);
                            alert('Bạn đã thêm ' + quantityToAdd + ' sản phẩm vào giỏ hàng');
                            location.reload();
                        });
                    } else {
                        alert('Số lượng không hợp lệ. Vui lòng nhập số nguyên dương.');
                    }
                }
            } else {
                location.reload();
            }
        } else {
            alert('Có lỗi xảy ra. Vui lòng thử lại sau.');
        }
    });
}

function getSelectedItems() {
    var selectedItems = [];
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            var itemId = checkboxes[i].dataset;
            selectedItems.push(itemId);
        }
    }
    return selectedItems;
}
