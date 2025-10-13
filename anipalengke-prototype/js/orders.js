// Orders, cart, and checkout simulation
(function(){
  const { readJson, writeJson, generateId, getCurrentUser, formatCurrency } = window.AniP;
  const { getProducts, updateProduct } = window.ProductsStore;

  function keyCart(userId){ return `cart_${userId}`; }

  function getCart(userId){ return readJson(keyCart(userId), []); }
  function setCart(userId, items){ writeJson(keyCart(userId), items); }

  function addToCart(productId, quantity){
    const user = getCurrentUser();
    const items = getCart(user.id);
    const existing = items.find(i => i.productId === productId);
    if (existing) existing.quantity += quantity; else items.push({ productId, quantity });
    setCart(user.id, items);
    return items;
  }

  function removeFromCart(productId){
    const user = getCurrentUser();
    const items = getCart(user.id).filter(i => i.productId !== productId);
    setCart(user.id, items);
    return items;
  }

  function clearCart(userId){ setCart(userId, []); }

  function getOrders(){ return readJson('orders', []); }
  function setOrders(orders){ writeJson('orders', orders); }

  function checkout(){
    const user = getCurrentUser();
    const cart = getCart(user.id);
    if (!cart.length) throw new Error('Cart is empty');
    const products = getProducts();
    const items = cart.map(ci => {
      const p = products.find(pp => pp.id === ci.productId);
      return { productId: p.id, name: p.name, price: p.price, quantity: ci.quantity, farmerId: p.farmerId };
    });
    const total = items.reduce((s, it) => s + (it.price * it.quantity), 0);
    const order = { id: generateId('ord'), buyerId: user.id, buyerName: user.name, items, total, status: 'Paid', createdAt: Date.now() };
    const orders = getOrders();
    orders.unshift(order);
    setOrders(orders);

    // decrement stock
    items.forEach(it => {
      const current = products.find(p => p.id === it.productId);
      if (current) updateProduct(current.id, { stock: Math.max(0, Number(current.stock) - Number(it.quantity)) });
    });

    clearCart(user.id);
    return order;
  }

  function getOrdersForUser(user){
    const all = getOrders();
    if (user.role === 'buyer') return all.filter(o => o.buyerId === user.id);
    if (user.role === 'farmer') return all.filter(o => o.items.some(i => i.farmerId === user.id));
    return all; // admin
  }

  function formatOrderRow(order){
    const itemSummary = order.items.map(i => `${i.name} x${i.quantity}`).join(', ');
    return `<tr>
      <td>${order.id}</td>
      <td>${order.buyerName}</td>
      <td>${itemSummary}</td>
      <td>${formatCurrency(order.total)}</td>
      <td><span class="tag">${order.status}</span></td>
      <td>${new Date(order.createdAt).toLocaleString()}</td>
    </tr>`;
  }

  window.OrdersStore = { getCart, addToCart, removeFromCart, clearCart, checkout, getOrders, getOrdersForUser, formatOrderRow };
})();
