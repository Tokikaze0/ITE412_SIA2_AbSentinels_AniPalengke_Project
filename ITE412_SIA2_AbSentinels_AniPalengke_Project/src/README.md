# AniPalengke – A Farmer-to-Buyer Marketplace and Farming Advisory System

This is a DFD Level 0-aligned prototype with Django backend, Vue 3 + Tailwind frontend, JSON-based mock databases, and a simple file-based pub/sub to simulate async events.

## Structure

```
src/
  backend/
    anipalengke_backend/
    authapp/          # Process 1.0 Authenticate User
    products/         # Process 2.0 Manage Products & Inventory
    orders/           # Process 3.0 Process Orders & Payments
    delivery/         # Process 4.0 Handle Logistics & Delivery
    notifications/    # Process 5.0 Notifications and Reports
    community/        # Process 6.0 Advisory Content and Community
    pubsubapp/        # Simple file-based pub/sub
    utils/            # JSON DB, JWT, CORS middleware
    manage.py
    requirements.txt
  frontend/
    index.html
    vite.config.js
    package.json
    tailwind.config.js
    postcss.config.js
    src/
      main.js
      assets/main.css
      router/index.js
      services/api.js
      pages/*.vue
  data/
    users.json        # D1: User Database
    products.json     # D2: Product Database
    orders.json       # D3: Orders Database
    payments.json     # D3: Payments Database
    deliveries.json   # D4: Delivery Database
    community.json    # D5: Community Database
  pubsub/
    topics.json
```

## Backend (Django)

- Install dependencies:

```bash
pip install -r src/backend/requirements.txt
```

- Run server:

```bash
python src/backend/manage.py runserver 0.0.0.0:8000
```

Endpoints map directly to DFD processes:
- Auth: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`
- Products: `/api/products/`, `/api/products/{id}`
- Orders: `/api/orders/`
- Payments: `/api/payments/`
- Delivery: `/api/delivery/`, `/api/delivery/track`
- Notifications: `/api/notifications/`, `/api/notifications/consume`
- Community: `/api/community/`
- Advisory: `/api/advisory/`

## Frontend (Vue 3 + Tailwind)

- Install Node deps:

```bash
cd src/frontend
npm install
```

- Run dev server:

```bash
npm run dev
```

The dev server proxies `/api` to `http://localhost:8000`.

## Event Flow (Simulation)
- Creating an order publishes `OrderCreated`.
- Paying confirms and publishes `PaymentConfirmed`.
- Posting advisory publishes `NewAdvisoryPost`.
- Delivery `track` consumes `OrderCreated` to auto-create delivery entries.
- Notifications `consume` ingests events and appends to notifications log.

## Demo Flow
1. Auth → Login as `buyer@example.com` / `buyer123` or `farmer@example.com` / `farmer123`.
2. Products → Browse and create (as Farmer/Admin).
3. Orders → Create order and pay.
4. Delivery → Click "Consume Events" to auto-generate delivery records.
5. Notifications → Click "Consume" to see notifications.
6. Community → Create posts. Advisory → Publish advisory and then check Notifications again.

Notes:
- This prototype uses JSON files for persistence and a file-based pub/sub. Replace with real DB and message broker when productionizing.
- JWT is demo-grade; don't reuse secrets in production.
