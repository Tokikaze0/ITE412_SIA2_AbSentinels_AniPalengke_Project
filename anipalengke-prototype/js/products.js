// Products store and helpers
(function(){
  const { readJson, writeJson, generateId, getCurrentUser } = window.AniP;

  function seedProducts(){
    if (readJson('products', null)) return;
    const users = window.UsersStore.getUsers();
    const farmer1 = users.find(u => u.role === 'farmer');
    const products = [
      { id: generateId('prd'), name: 'Cassava', price: 50, stock: 30, farmerId: farmer1?.id, farmer: farmer1?.name || 'Juan Dela Cruz', image: 'assets/placeholder.jpg' },
      { id: generateId('prd'), name: 'Tilapia', price: 120, stock: 20, farmerId: farmer1?.id, farmer: farmer1?.name || 'Juan Dela Cruz', image: 'assets/placeholder.jpg' },
      { id: generateId('prd'), name: 'Eggplant', price: 40, stock: 60, farmerId: farmer1?.id, farmer: farmer1?.name || 'Juan Dela Cruz', image: 'assets/placeholder.jpg' }
    ];
    writeJson('products', products);
  }
  function getProducts(){ return readJson('products', []); }
  function setProducts(products){ writeJson('products', products); }

  function addProduct({ name, price, stock, image }){
    const user = getCurrentUser();
    const products = getProducts();
    const item = { id: generateId('prd'), name, price: Number(price), stock: Number(stock), farmerId: user?.id, farmer: user?.name, image: image || 'assets/placeholder.jpg' };
    products.push(item);
    setProducts(products);
    return item;
  }

  function updateProduct(id, changes){
    const products = getProducts();
    const idx = products.findIndex(p => p.id === id);
    if (idx === -1) return null;
    products[idx] = { ...products[idx], ...changes };
    setProducts(products);
    return products[idx];
  }

  function deleteProduct(id){
    const products = getProducts().filter(p => p.id !== id);
    setProducts(products);
  }

  function searchProducts(query){
    const q = String(query || '').toLowerCase();
    return getProducts().filter(p => p.name.toLowerCase().includes(q) || p.farmer?.toLowerCase().includes(q));
  }

  window.ProductsStore = { seedProducts, getProducts, addProduct, updateProduct, deleteProduct, searchProducts };

  document.addEventListener('DOMContentLoaded', seedProducts);
})();
