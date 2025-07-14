let modalQt = 1;
let cart = [];
let modalKey = 0;

const c = (el) => document.querySelector(el);
const cs = (el) => document.querySelectorAll(el);

// --- FUNÇÕES AUXILIARES ---
const formatPrice = (price) => `R$ ${price.toFixed(2).replace('.', ',')}`;
const closeModal = () => {
    c('.pizzaWindowArea').style.opacity = 0;
    setTimeout(() => { c('.pizzaWindowArea').style.display = 'none'; }, 200);
};

// --- LÓGICA DO MODAL ---
function updatePrice() {
    const pizza = pizzaJson[modalKey];
    const sizeIndex = parseInt(c('.pizzaInfo--size.selected').getAttribute('data-key'));
    let price = pizza.price;
    if (sizeIndex === 0) price *= 0.85; // Pequena
    if (sizeIndex === 2) price *= 1.15; // Grande
    c('.pizzaInfo--actualPrice').innerHTML = formatPrice(price * modalQt);
}

function openModal(key) {
    modalKey = key;
    modalQt = 1;
    const pizza = pizzaJson[key];

    c('.pizzaBig img').src = pizza.img;
    c('.pizzaInfo h1').innerHTML = pizza.name;
    c('.PizzaInfo--desc').innerHTML = pizza.description;
    c('.pizzaInfo--qt').innerHTML = modalQt;

    cs('.pizzaInfo--size').forEach((size, sizeIndex) => {
        if (sizeIndex === 1) size.classList.add('selected'); else size.classList.remove('selected');
        // --- ESTA É A LINHA QUE FAZ A MÁGICA ---
        // Ela preenche o 'span' com a informação de tamanho vinda do pizzas.js
        size.querySelector('span').innerHTML = pizza.sizes[sizeIndex];
    });
    
    updatePrice();

    c('.pizzaWindowArea').style.opacity = 0;
    c('.pizzaWindowArea').style.display = 'flex';
    setTimeout(() => c('.pizzaWindowArea').style.opacity = 1, 100);
}

// --- LÓGICA DO CARRINHO ---
function updateCart() {
    const menuOpener = c('.menu-opener span');
    if (menuOpener) {
        menuOpener.innerHTML = cart.length;
    }

    if (cart.length > 0) {
        c('aside').classList.add('show');
        c('.cart').innerHTML = '';
        let subtotal = 0, desconto = 0, total = 0;

        for (let i in cart) {
            let pizzaItem = pizzaJson.find(item => item.id == cart[i].id);
            let itemPrice = pizzaItem.price;
            if (cart[i].size === 0) itemPrice *= 0.85;
            if (cart[i].size === 2) itemPrice *= 1.15;
            subtotal += itemPrice * cart[i].qt;

            let cartItem = c('.models .cart--item').cloneNode(true);
            let pizzaSizeName;
            switch(cart[i].size) {
                case 0: pizzaSizeName = 'P'; break;
                case 1: pizzaSizeName = 'M'; break;
                case 2: pizzaSizeName = 'G'; break;
            }
            cartItem.querySelector('img').src = pizzaItem.img;
            cartItem.querySelector('.cart--itemName').innerHTML = `${pizzaItem.name} (${pizzaSizeName})`;
            cartItem.querySelector('.cart--itemQt--qt').innerHTML = cart[i].qt;
            
            cartItem.querySelector('.cart--itemQt--minus').addEventListener('click', () => {
                if (cart[i].qt > 1) cart[i].qt--; else cart.splice(i, 1);
                updateCart();
            });
            cartItem.querySelector('.cart--itemQt--plus').addEventListener('click', () => {
                cart[i].qt++;
                updateCart();
            });
            c('.cart').append(cartItem);
        }
        desconto = subtotal * 0.1;
        total = subtotal - desconto;
        c('.cart--details--subTotal span').innerHTML = formatPrice(subtotal);
        c('.cart--details--discount span').innerHTML = formatPrice(desconto);
        c('.cart--details--total span').innerHTML = formatPrice(total);
    } else {
        c('aside').classList.remove('show');
        c('aside').style.left = '100vw';
    }
}

// --- EVENTOS ---
// 1. Renderização inicial das pizzas
pizzaJson.map((item, index) => {
    let pizzaItem = c('.models .pizza-item').cloneNode(true);
    pizzaItem.setAttribute('data-key', index);
    pizzaItem.querySelector('.pizza-item--img img').src = item.img;
    pizzaItem.querySelector('.pizza-item--price').innerHTML = formatPrice(item.price);
    pizzaItem.querySelector('.pizza-item--name').innerHTML = item.name;
    pizzaItem.querySelector('.pizza-item--desc').innerHTML = item.description;
    pizzaItem.querySelector('a').addEventListener('click', (e) => {
        e.preventDefault();
        openModal(index);
    });
    c('.pizza-area').append(pizzaItem);
});

// 2. Eventos do Modal
cs('.pizzaInfo--cancelButton, .pizzaInfo--CancelMobileButton').forEach(item => item.addEventListener('click', closeModal));
c('.pizzaInfo--qtminus').addEventListener('click', () => {
    if (modalQt > 1) { modalQt--; c('.pizzaInfo--qt').innerHTML = modalQt; updatePrice(); }
});
c('.pizzaInfo--qtplus').addEventListener('click', () => {
    modalQt++; c('.pizzaInfo--qt').innerHTML = modalQt; updatePrice();
});
cs('.pizzaInfo--size').forEach(size => {
    size.addEventListener('click', () => {
        c('.pizzaInfo--size.selected').classList.remove('selected');
        size.classList.add('selected');
        updatePrice();
    });
});
c('.pizzaInfo--addButton').addEventListener('click', () => {
    const size = parseInt(c('.pizzaInfo--size.selected').getAttribute('data-key'));
    const identifier = pizzaJson[modalKey].id + '@' + size;
    const key = cart.findIndex(item => item.identifier === identifier);
    if (key > -1) {
        cart[key].qt += modalQt;
    } else {
        cart.push({ identifier, id: pizzaJson[modalKey].id, size, qt: modalQt });
    }
    updateCart();
    closeModal();
});

// 3. Eventos do Carrinho
c('.menu-opener').addEventListener('click', () => {
    if (cart.length > 0) { updateCart(); c('aside').style.left = '0'; }
});
c('.menu-closer').addEventListener('click', () => { c('aside').style.left = '100vw'; });

// 4. Finalizar Pedido
c('.cart--button').addEventListener('click', () => {
    if (cart.length === 0) { alert("Seu carrinho está vazio!"); return; }
    const orderData = cart.map((cartItem) => {
        const pizza = pizzaJson.find(p => p.id == cartItem.id);
        let sizeName; let itemPrice = pizza.price;
        switch(cartItem.size) {
            case 0: sizeName = 'P'; itemPrice *= 0.85; break;
            case 1: sizeName = 'M'; break;
            case 2: sizeName = 'G'; itemPrice *= 1.15; break;
        }
        return { name: pizza.name, size: sizeName, qt: cartItem.qt, price: itemPrice };
    });
    fetch('/api/pedidos/criar', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(orderData) })
    .then(res => {
        if (res.status === 401) { alert("Você precisa estar logado para finalizar o pedido."); window.location.href = '/login'; return null; }
        return res.json();
    }).then(data => {
        if (data && data.success) {
            alert(`Pedido #${data.pedido_id} realizado!`);
            cart = []; updateCart(); window.location.href = '/meus-pedidos';
        } else if (data && data.error) { alert('Erro: ' + data.error); }
    }).catch(err => {
        if (err && err.name !== 'AbortError' && !err.message.includes('JSON')) {
             console.error('Erro ao finalizar pedido:', err);
        }
    });
});