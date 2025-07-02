let modalQt = 1;
let modalKey = 0;
let pizzaList = [];

const c = (el) => document.querySelector(el);
const cs = (el) => document.querySelectorAll(el);

function formatPrice(price) {
    return `${price.toLocaleString('pt-br', {style: 'currency', currency: 'BRL'})}`;
}

function closeModal() {
    c('.pizzaWindow').style.opacity = 0;
    setTimeout(() => {
        c('.pizzaWindow').style.display = 'none';
    }, 500);
}

function updateCart() {
    c('.menu-opener span').innerHTML = pizzaList.length;

    if (pizzaList.length > 0) {
        c('aside').classList.add('show');
        c('.cart').innerHTML = '';

        let subtotal = 0;
        let discount = 0;
        let total = 0;

        for (let i in pizzaList) {
            let pizzaItem = pizzaJson.find((item) => item.id == pizzaList[i].id);

            subtotal += (pizzaItem.price * pizzaList[i].qt);

            let cartItem = c('.models .cart--item').cloneNode(true);

            let pizzaSizeName;
            switch(pizzaList[i].size) {
                case 0:
                    pizzaSizeName = 'P';
                break;
                case 1:
                    pizzaSizeName = 'M';
                break;
                case 2:
                    pizzaSizeName = 'G';
                break
            }
            let pizzaName = `${pizzaItem.name} (${pizzaSizeName})`;

            cartItem.querySelector('img').src = pizzaItem.img;
            cartItem.querySelector('.cart--itemName').innerHTML = pizzaName;
            cartItem.querySelector('.cart--itemQt--qt').innerHTML = pizzaList[i].qt;
            cartItem.querySelector('.cart--itemQt--minus').addEventListener('click', () => {
                if (pizzaList[i].qt > 1) {
                    pizzaList[i].qt--;
                } else {
                    pizzaList.splice(i, 1)
                }
                updateCart();
            });
            cartItem.querySelector('.cart--itemQt--plus').addEventListener('click', () => {
                pizzaList[i].qt++;
                updateCart();
            })

            c('.cart').appendChild(cartItem);
        }
        discount = subtotal * 0.1;
        total = subtotal - discount;

        c('.cart--details--subTotal span').innerHTML = formatPrice(subtotal);
        c('.cart--details--discount span').innerHTML = formatPrice(discount);
        c('.cart--details--total span').innerHTML = formatPrice(total);
    } else {
        c('aside').classList.remove('show');
        c('aside').style.left = '100vw';
    }
}

pizzaJson.map((item, index) => {
    let pizzaModels = c('.models .pizza-item').cloneNode(true);

    pizzaModels.setAttribute('data-key', index);
    pizzaModels.querySelector('.pizza-item--img img').src = item.img;
    pizzaModels.querySelector('.pizza-item--price').innerHTML = formatPrice(item.price);
    pizzaModels.querySelector('.pizza-item--name').innerHTML = item.name;
    pizzaModels.querySelector('.pizza-item--desc').innerHTML = item.description;
    pizzaModels.querySelector('a').addEventListener('click', (e) => {
        e.preventDefault();
        let key = e.target.closest('.pizza-item').getAttribute('data-key');
        modalQt = 1;
        modalKey = key;
        c('.pizzaWindow').style.display = 'flex';

        c('.pizzaBig img').src = pizzaJson[key].img;
        c('.pizzaInfo h1').innerHTML = pizzaJson[key].name;
        c('.PizzaInfo--desc').innerHTML = pizzaJson[key].description;
        c('.pizzaInfo--actualPrice').innerHTML = formatPrice(pizzaJson[key].price);
        c('.pizzaInfo--size.selected').classList.remove('selected');

        cs('.pizzaInfo--size').forEach((size, sizeIndex) => {
            if (sizeIndex == 2) {
                size.classList.add('selected')
            }
            size.querySelector('span').innerHTML = `${pizzaJson[key].sizes[sizeIndex]}`;
        });
        c('.pizzaInfo--qt').innerHTML = modalQt;

        c('.pizzaWindow').style.opacity = 0;
        c('.pizzaWindow').style.display = 'flex';
        setTimeout(() => {
            c('.pizzaWindow').style.opacity = 1;
        }, 200)
    });

    c('main .container').appendChild(pizzaModels);
});

cs('.pizzaInfo--cancelButton, .pizzaInfo--CancelMobileButton').forEach((item) => {
    item.addEventListener('click', closeModal);
})

cs('.pizzaInfo--qtminus, .pizzaInfo--qtplus').forEach((item) => {
    item.addEventListener('click', () => {
        switch (item.innerHTML) {
            case '-':
                if (modalQt > 1) {
                    modalQt--;
                }
            break;
            case '+':
                modalQt++;
            break;
        }
        c('.pizzaInfo--qt').innerHTML = modalQt;
    })
});

cs('.pizzaInfo--size').forEach((size, sizeIndex) => {
    size.addEventListener('click', () => {
        c('.pizzaInfo--size.selected').classList.remove('selected');
        size.classList.add('selected');
    });
});

c('.menu-opener').addEventListener('click', (e) => {
    if (pizzaList.length > 0) {
        c('aside').style.left = '0';
    }
});

c('.menu-closer').addEventListener('click', () => {
    c('aside').style.left = '100vw';
})

c('.pizzaInfo--addButton').addEventListener('click', (e) => {
    let size = parseInt(c('.pizzaInfo--size.selected').getAttribute('data-key'));
    let identifier = pizzaJson[modalKey].id + '@' + size;
    let key = pizzaList.findIndex(item => item.identifier === identifier);
    if (key > -1) {
        pizzaList[key].qt += modalQt;
    } else {
        pizzaList.push({
            identifier,
            id: pizzaJson[modalKey].id,
            size,
            qt: modalQt
        });
    }
    closeModal();
    updateCart();
});