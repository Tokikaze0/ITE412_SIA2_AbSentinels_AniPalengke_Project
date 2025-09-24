# Project Overview

## 1. System Objectives

### What problem are you solving?
The agricultural sector faces significant challenges in connecting farmers directly with buyers, leading to price opacity, reduced margins for farmers, and limited access to market information. Traditional supply chains often involve multiple intermediaries, resulting in farmers receiving lower prices while buyers pay higher costs.

### Who benefits and how?
- **Farmers**: Gain direct access to buyers, improved price transparency, and higher margins through reduced intermediaries
- **Buyers**: Access to verified, quality produce with transparent pricing and reliable delivery
- **Marketplace Admins**: Comprehensive tools for monitoring marketplace health, managing disputes, and ensuring compliance
- **Agricultural Community**: Access to localized farming tips, price bulletins, and seasonal advisories for better decision-making

## 2. Proposed Scope

### Modules/systems to integrate:
- **Authentication & Authorization**: User registration, login, role-based access control
- **User Management**: Profile management, verification, and account administration
- **Product Catalog**: Listing management, inventory tracking, and search functionality
- **Order Management**: Cart, checkout, order lifecycle, and status tracking
- **Payment Processing**: Integration with payment gateways for secure transactions
- **Logistics Integration**: Delivery request handling and tracking
- **Notification System**: In-app, email, and SMS notifications
- **Content Management**: Price bulletins and farming tips hub
- **Review & Rating System**: Feedback mechanism for trust building
- **Analytics & Reporting**: Admin dashboards and business intelligence

### In-scope features for Lab 1–3:
- Core user authentication and role management
- Basic product listing and search functionality
- Order placement and payment processing
- Essential notification system
- Basic admin dashboard

### Out-of-scope (for now):
- Advanced analytics and AI-driven recommendations
- Mobile application development
- Advanced logistics optimization
- Multi-language support
- Advanced dispute resolution automation

## 3. Stakeholders

- **Farmers** — Need to list products, manage inventory, receive orders, and get fair pricing
- **Buyers** — Need to search products, place orders, make payments, and track deliveries
- **Marketplace Admins** — Need to verify users, moderate content, manage disputes, and monitor system health
- **Payment Gateway Providers** — Need to process secure transactions and provide confirmation services
- **Logistics Providers** — Need to receive delivery requests and provide tracking information
- **Agricultural Extension Offices** — Need to provide farming tips and market price information
- **System Administrators** — Need to maintain system performance, security, and compliance

## 4. Tools & Technologies

### Languages/Frameworks:
- **Frontend**: Vue.js for responsive web interface
- **Backend**: Python with Django/FastAPI
- **Database**: Firebase for relational data, Redis for caching

### Integration approach:
- **REST APIs**: Primary communication protocol between services
- **Webhooks**: Real-time event notifications to external services
- **Message Queue**: Asynchronous processing for notifications and background tasks
- **API Gateway**: Centralized API management and rate limiting

### Repos/Services:
- **Version Control**: GitHub for source code management
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Cloud Platform**: Hostinger for hosting and infrastructure
- **Monitoring**: Application performance monitoring and logging services

### Testing tools:
- **Unit Testing**: pytest (Python)
- **Integration Testing**: Supertest for API testing
- **End-to-End Testing**: Playwright
- **Load Testing**: Artillery for performance testing

### Additional Tools:
- **Documentation**: Markdown with automated API documentation
- **Security**: OAuth 2.0 for authentication, JWT for authorization
- **Payment Integration**: Gcash for payment processing
- **Notification Services**: SendGrid for email, Twilio for SMS
- **File Storage**: AWS S3 or Azure Blob Storage for images and documents

## 5. High-Level System Overview

### 5.1 Major Modules/Subsystems
- **Product Catalog & Order Management**  
  Farmers can publish produce listings, manage inventory, and update prices. Buyers can browse items, add them to the cart, and complete purchases. The system tracks the full order lifecycle from creation to fulfillment.  

- **Payment & Settlement System**  
  Integrated with secure payment gateways (e.g., GCash, PayMaya) to handle transactions between buyers and farmers. Ensures traceable payouts, refund management, and transaction verification.  

- **Admin & Analytics Dashboard**  
  Administrators oversee user onboarding, identity verification, dispute management, and overall platform monitoring. Dashboards provide analytics, seasonal advisories, and farming tips to support decision-making.  

---

### 5.2 External Systems/Interfaces
- **Payment Gateway APIs** – GCash, PayMaya for secure digital payments  
- **Logistics Provider APIs** – Lalamove, GrabExpress for order shipment and delivery tracking  
- **Notification Services** – SendGrid (email), Twilio (SMS), Firebase Cloud Messaging (in-app alerts)  
- **Database & Storage** – Firebase (data storage), Redis (caching), AWS S3/Azure Blob Storage (images & documents)  
- **Optional APIs** – OpenWeatherMap for weather updates, Department of Agriculture data for localized crop pricing  

---

### 5.3 Data Flow Summary
1. **User Registration & Login** – Farmers, buyers, and admins register and authenticate through the system.  
2. **Product Listing & Browsing** – Farmers add product details to the catalog, which buyers can search and view in real time.  
3. **Order & Payment**

## 6. Integration Pattern Applied

**Integration Pattern:** Publish–Subscribe (Pub–Sub)

**Rationale:**  
AniPalengke is both an **e-commerce platform** and a **farming advisory/community system**. Each part generates events that must be shared with multiple services:

- When an **order is created**, the Notification Service informs farmers and buyers, the Logistics Service prepares delivery, and Analytics records sales data.  
- When a **payment is confirmed**, buyers are notified, farmer balances are updated, and financial logs are recorded.  
- When an **advisory post or farming tip is published**, other farmers are notified, Analytics tracks engagement, and admins may review content.  

The **Pub–Sub pattern** supports this by:  
- **Decoupling** producers (Order, Payment, Advisory services) from consumers (Notifications, Analytics, Logistics).  
- **Scalability**, since many services can react to the same event independently.  
- **Flexibility**, allowing new services (e.g., AI recommendations, government advisory agencies) to subscribe without changing existing modules.  
- **Reliability**, because the broker queues events if a consumer is temporarily unavailable.  

AniPalengke uses **REST APIs** for synchronous operations (login, profile updates, catalog browsing) and **Pub–Sub messaging** for asynchronous communication (orders, payments, advisory events). This ensures the platform is **responsive, resilient, and community-driven**.  

**Diagram Reference:** `HighLevelArch.png`
