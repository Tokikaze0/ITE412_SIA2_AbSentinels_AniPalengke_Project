import Auth from '../pages/Auth.vue'
import Products from '../pages/Products.vue'
import Orders from '../pages/Orders.vue'
import Delivery from '../pages/Delivery.vue'
import Notifications from '../pages/Notifications.vue'
import Community from '../pages/Community.vue'
import Advisory from '../pages/Advisory.vue'

export default [
  { path: '/', redirect: '/products' },
  { path: '/auth', component: Auth },
  { path: '/products', component: Products },
  { path: '/orders', component: Orders },
  { path: '/delivery', component: Delivery },
  { path: '/notifications', component: Notifications },
  { path: '/community', component: Community },
  { path: '/advisory', component: Advisory },
]
