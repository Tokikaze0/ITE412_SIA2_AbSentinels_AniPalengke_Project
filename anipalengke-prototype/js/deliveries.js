// Delivery tracking simulation
(function(){
  const { readJson, writeJson, generateId } = window.AniP;

  function seedDeliveries(){
    if (readJson('deliveries', null)) return;
    writeJson('deliveries', []);
  }
  function getDeliveries(){ return readJson('deliveries', []); }
  function setDeliveries(list){ writeJson('deliveries', list); }

  function createDelivery(orderId){
    const deliveries = getDeliveries();
    const d = { id: generateId('dlv'), orderId, status: 'Preparing', progress: 0, timeline: [{ ts: Date.now(), label: 'Preparing order' }] };
    deliveries.unshift(d);
    setDeliveries(deliveries);
    return d;
  }

  function simulateProgress(deliveryId, onUpdate){
    const timer = setInterval(() => {
      const list = getDeliveries();
      const idx = list.findIndex(d => d.id === deliveryId);
      if (idx === -1) return clearInterval(timer);
      const d = list[idx];
      d.progress = Math.min(100, d.progress + Math.floor(Math.random()*15 + 10));
      if (d.progress >= 100) {
        d.progress = 100;
        d.status = 'Delivered';
        d.timeline.push({ ts: Date.now(), label: 'Delivered' });
        clearInterval(timer);
      } else if (d.progress > 60) {
        d.status = 'Out for delivery';
      } else if (d.progress > 20) {
        d.status = 'In transit';
      }
      list[idx] = d;
      setDeliveries(list);
      if (onUpdate) onUpdate(d);
    }, 1000);
    return timer;
  }

  window.DeliveryStore = { seedDeliveries, getDeliveries, createDelivery, simulateProgress };
  document.addEventListener('DOMContentLoaded', seedDeliveries);
})();
