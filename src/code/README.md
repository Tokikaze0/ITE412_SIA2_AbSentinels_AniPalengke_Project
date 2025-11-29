# AniPalengke - Django Prototype

This is a Django prototype for the AniPalengke agricultural marketplace.

## Setup

1.  **Environment**: Ensure you have Python installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database**:
    Run migrations to setup the local SQLite database for Authentication and Sessions.
    ```bash
    python manage.py migrate
    ```
4.  **Firebase (Optional)**:
    To use real Firestore data instead of mock data:
    -   Place your `serviceAccountKey.json` file in the project root (`anipalengke/`).
    -   The app will automatically detect it and switch to Firestore.

## Running the Server

```bash
python manage.py runserver
```

## Features

-   **Authentication**: Register and Login as Farmer, Buyer, or Admin.
-   **Products**: Browse products (Mock data or Firestore).
-   **Cart**: Add items to cart (Session-based).
-   **Checkout**: Mock checkout process.
-   **Dashboards**: Role-based dashboards for Farmer, Buyer, and Admin.
-   **Analytics**: Chart.js integration in Admin Dashboard.

## Project Structure

-   `core/`: Base templates, static files, and Firestore utilities.
-   `users/`: Authentication and Profile management.
-   `products/`: Product catalog and search.
-   `orders/`: Cart and Checkout logic.
