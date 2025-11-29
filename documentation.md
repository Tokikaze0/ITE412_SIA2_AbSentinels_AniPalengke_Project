
ANIPALENGKE: AN AGRICULTURAL MARKETPLACE
& FARMING SUPPORT PLATFORM




A Final Project
Presented to the Faculty of the 
Bachelor of Science in Information Technology
Mindoro State University—Main Campus


In Partial Fulfillment of the Requirements
for System Integration and Architecture 2



By
Arwin R. Madeja
Aerone John P. Grefalda
Jan Russel S. Salazar


Dr. Cirile Dominic A. Horlador
ITE412 Professor



December 2025




DOCUMENTATION OUTLINE


1.	Executive Summary
•	Project Overview: AniPalengke is a web-based marketplace platform designed to digitize local markets by enabling vendors and customers to interact through an online system. The project addresses difficulties faced by traditional markets such as limited visibility, manual transactions, and lack of centralized digital management.
•	Main Features: The system provides essential marketplace functionalities, beginning with vendor registration and product management, allowing sellers to create accounts, list items, and maintain accurate product information. Customers can browse available products through an organized interface and manage their selections using a built-in cart system. Once ready, users can proceed with order placement, after which the system handles the basic processing workflow for both vendors and customers. Administrators are given oversight capabilities, enabling them to configure system settings, manage user accounts, and monitor marketplace activities. Additionally, the platform integrates APIs and external services such as mapping tools and notification systems to enhance overall user experience and improve operational efficiency.
•	Outcome: The system provides an organized, digitized way of managing local marketplace operations, increasing accessibility for users and expanding vendor reach. It demonstrates integration concepts and real-world application potential.
2.	Target Organization and Use Case

•	Organization Identification: The client is the Pagkakaisa Farmers Association, a small group of local farmers and vendors in the community. They mainly sell their products in traditional markets and still use manual methods for listing items, handling customers, and managing orders. AniPalengke will help them move to a more modern and easier online system so they can reach more customers and manage their products better.
•	Organizational Need or Problem: The Pagkakaisa Farmers Association currently faces challenges because most of their processes are manual. Farmers list their products by hand, customers must visit the market physically to buy goods, and there is no organized system to track orders or product availability. This causes delays, misunderstandings, and limited customer reach. The organization needs a digital platform that will help them display their products online, manage orders more easily, and connect with more buyers without relying only on physical market visits.
•	Current Business Process Flow: Below is the current process of the Pagkakaisa Farmers Association before using the system:
	Farmers harvest and prepare their products.

	They bring the products to the physical market.

	Customers visit the market to check the available items.

	Customers ask prices and choose items manually.

	Payment is done in cash with no formal tracking.

	Farmers keep manual records of what was sold and what remains.


3.	Project Objectives and Scope
•	Objectives: This project aims to develop a functional and integrated online marketplace platform that supports the needs of the Pagkakaisa Farmers Association. Specifically, it aims to:
o	To create an online platform where farmers can register and manage their products.
o	To provide customers with a simple way of browsing items and placing orders.
o	To integrate essential system components such as vendor management, customer cart, and order processing.
o	To demonstrate system integration using APIs and connected modules.
•	Scope: The scope of the AniPalengke system focuses on creating an online ordering platform for the Pagkakaisa Farmers Association. Customers can browse products, place orders online, and choose between picking up their items at the designated market location or having them delivered via integrated logistics services. The system includes vendor management, product listings, customer cart functionality, order placement, and basic admin controls.
The project also integrates specific APIs and services, including Firebase for database and firebase cloud messaging for notification services, Google Authentication for secure login, GCash payment method via PayMongo for simplified transactions, Lalamove API for delivery logistics, and a geological mapping API for locating pickup points or market areas.
4.	Assumptions and Limitations: This project assumes that users can access the system with a stable internet connection and that the external services used such as Google Authentication, GCash and bank payments, and the geological mapping API are available and running properly. It is also assumed that customers understand that there is no delivery option and all orders must be picked up at the market. Vendors are expected to update their product quantities and prices when needed.
5.	System Architecture and Design
•	System Architecture Diagram:
o	A diagram showing the overall system architecture, integration points, and data flow between components.
	Flow chart
	Data Flow Diagram
	Entity-Relationship Diagram

	Use-Case Diagram
	System Architecture
•	Modules and Components: The system is composed of several key modules:
    o   **User Management (Users App):** Handles authentication (via Google/Firebase), profile management, and role-based access control (Farmer, Buyer, Admin).
    o   **Marketplace (Products & Orders Apps):** Manages product listings, inventory, shopping cart, checkout processes, and order tracking. It integrates with Firestore for real-time inventory updates.
    o   **Community & Chat:** Provides a social platform for farmers to share knowledge (posts/comments) and a real-time messaging system for buyer-seller communication.
    o   **AI Services (Core App):** Leverages Google Gemini 2.0 Flash for intelligent features such as crop identification from images, product validation, and a farming assistant chatbot.
    o   **Logistics & Payments:** Dedicated modules for handling delivery quotes (Lalamove) and secure payments (PayMongo/GCash).

•	Integration Patterns and Tools: The AniPalengke system follows a Modular Architecture:
    o   **Django Monolith:** Serves as the core web server, handling business logic, routing, and serving server-side rendered templates.
    o   **Firebase Backend-as-a-Service (BaaS):** Acts as the primary data store (Firestore) and handles client-side authentication and real-time updates.
    o   **External APIs:** The system acts as a client to various third-party services (Lalamove, PayMongo, Gemini) using RESTful HTTP requests.
    o   **MVC Structure:** Within Django, the standard Model-View-Controller (MVT in Django terms) is preserved, but the "Model" layer is abstracted to communicate with Firestore instead of a traditional SQL database for dynamic data.

6.	Technology Stack
•	Backend: Django (Python).
•	Frontend: Django Templates, HTML5, CSS3, JavaScript (ES6+).
•	Database: Firebase Firestore (NoSQL) for flexibility and real-time capabilities.
•	APIs and External Services: 
    o   **Database & Auth:** Firebase Firestore, Firebase Authentication.
    o   **AI & ML:** Google Gemini 2.0 Flash (Generative AI).
    o   **Payments:** PayMongo API (GCash, GrabPay).
    o   **Logistics:** Lalamove API (Delivery Quotes & Booking).
    o   **Mapping:** Google Maps API / Geological Mapping tools.
•	Other Tools: GitHub (VCS), VS Code (IDE), Postman (API Testing).

7.	Functional Specifications
•	Feature List:
    1.  **Smart Product Listing:** Farmers can upload product photos. The system uses Gemini AI to analyze the image, verify if it's a valid crop, and suggest categories automatically.
    2.  **Dynamic Marketplace:** Buyers can search products with filters (Location, Category) and view real-time stock availability.
    3.  **Integrated Checkout:**
        *   **Logistics:** Users receive real-time delivery quotes from Lalamove based on their location.
        *   **Payments:** Secure payment processing via PayMongo (GCash), with support for Cash on Delivery (COD).
    4.  **Community Feed:** A social space for farmers to post updates, ask questions, and interact via comments.
    5.  **Real-time Chat:** Direct messaging between buyers and farmers to negotiate prices or ask product details.

•	User Interface (UI):
    *   **Dashboard:** A central hub showing recent orders, sales stats (for farmers), and recommended products (for buyers).
    *   **Marketplace Grid:** A clean, card-based layout displaying product images, prices, and farmer locations.
    *   **Chat Interface:** A familiar messaging layout with conversation lists and real-time message bubbles.

•	Data Flow and Interaction:
    1.  **User Action:** User submits a product form with an image.
    2.  **Django View:** Receives the request, saves the image temporarily.
    3.  **AI Processing:** Calls `core.ai.analyze_image` to validate the crop.
    4.  **Database Write:** If valid, saves metadata to Firestore `products` collection.
    5.  **Feedback:** User receives a success message and the product appears in the feed.

•	Error Handling:
    *   **Graceful Degradation:** If external APIs (e.g., Lalamove) are down, the system falls back to manual shipping calculations or "Pickup Only" mode.
    *   **Input Validation:** AI validates product relevance; Forms validate data types.
    *   **Logging:** Critical errors (API failures, DB connection issues) are logged to the console/server logs for debugging.
8.	Implementation Details
•	Core Code Excerpts:
    *   **AI Crop Validation (core/ai.py):**
        ```python
        def validate_crop(product_name, description, image_path=None):
            configure_gemini()
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = [
                f"Analyze this product: {product_name}. Is it a valid agricultural crop?",
                "Return JSON: {'is_valid': boolean, 'reason': string}"
            ]
            # ... image processing ...
            return model.generate_content(prompt).text
        ```
    *   **Lalamove Integration (orders/lalamove.py):**
        ```python
        def _generate_signature(self, method, path, body=""):
            time_stamp = int(time.time() * 1000)
            raw_signature = f"{time_stamp}\r\n{method}\r\n{path}\r\n\r\n{body}"
            signature = hmac.new(
                self.secret.encode(), raw_signature.encode(), hashlib.sha256
            ).hexdigest()
            return time_stamp, signature
        ```

•	Integration Logic:
    **Firestore & Django:** Unlike standard Django apps, `models.py` files are minimal. Instead, `core/utils.py` acts as a Data Access Layer (DAL), wrapping Firestore calls (get, set, update) into Python functions. This allows Django views to interact with NoSQL data as if it were local objects.
    **Payment Flow:** The system generates a PayMongo checkout URL and redirects the user. Upon completion, the user is redirected back to a success view (`/orders/payment/success/`), which verifies the transaction status before updating the order in Firestore.

•	Security Measures:
    **API Key Restrictions:** Google Cloud API keys are restricted by HTTP Referrer to prevent unauthorized usage.
    **Environment Variables:** Sensitive keys (Lalamove Secret, PayMongo Secret) are stored in a `.env` file and never committed to version control.
    **Firestore Rules:** Database access is strictly controlled via Security Rules (e.g., `allow write: if request.auth != null`), ensuring only authenticated users can modify data.

•	Challenges and Solutions:
    **Challenge:** Integrating a NoSQL database (Firestore) with Django's relational philosophy.
    **Solution:** Created a utility layer (`core/utils.py`) to map Firestore documents to Python dictionaries, mimicking Django model instances for templates.
    **Challenge:** verifying "real" crops from user uploads.
    **Solution:** Integrated Gemini 2.0 Flash to act as a content moderator, automatically rejecting non-agricultural uploads.

9.	Testing and Validation
•	Testing Strategy:
    **Unit Testing:** Testing individual utility functions (e.g., shipping calculators, AI prompt generation) to ensure logic correctness.
    **Integration Testing:** Verifying that the system communicates correctly with external APIs (Lalamove Sandbox, PayMongo Test Mode).
    **User Acceptance Testing (UAT):** Manual walkthroughs of the "Happy Path" (Register -> List Product -> Buy -> Checkout) to ensure flow consistency.

•	Test Cases and Results:
    | Test Case ID | Description | Expected Outcome | Status |
    | :--- | :--- | :--- | :--- |
    | TC-001 | User Registration (Google) | User is redirected to dashboard; Profile created in Firestore. | Passed |
    | TC-002 | Product Upload (Valid Crop) | AI returns `is_valid: true`; Product appears in marketplace. | Passed |
    | TC-003 | Product Upload (Invalid Image) | AI returns `is_valid: false`; Error message shown to user. | Passed |
    | TC-004 | Lalamove Quote Generation | System displays delivery fee based on mock locations. | Passed |
    | TC-005 | Checkout with GCash | User redirected to PayMongo; Order status updates to 'Paid' on return. | Passed |

•	User Feedback: Initial feedback from the Pagkakaisa Farmers Association highlighted the ease of use of the "Chat" feature, allowing them to quickly answer buyer inquiries. They also appreciated the "AI Auto-fill" for product categories, which saved them typing time.
•	Performance Metrics: Include any metrics for performance, such as response time or system load-handling capability.
10.	Deployment and Installation Guide
•	Deployment Instructions: Step-by-step guide for deploying the project, including any environment setup (e.g., cloud setup, server configuration).
•	Installation Requirements: List all software, hardware, or platforms required to run the project.
•	User Guide: Instructions on how to access and use the system’s functionalities, aimed at end-users or testers.
11.	Future Enhancements
•	Suggested Improvements: List any features, optimizations, or expansions that could be added to enhance the project.
•	Scalability Considerations: Discuss potential scalability improvements if the system were to be deployed at a larger scale.
•	New Integrations: Identify other systems or APIs that could add value to the project in future iterations.
 

12.	Conclusion and Reflection
•	Project Summary: Recap the project’s objectives, accomplishments, and overall impact.
•	Lessons Learned: Describe what students learned from this project, especially related to systems integration challenges and techniques.
•	Project Reflections: Reflect on how the project aligned with the course outcomes and any personal or technical growth achieved.
13.	Appendices
•	Complete Codebase: Include the full project code as an appendix or provide a link to a GitHub repository.
•	System Configurations: Details of system configurations used, such as environment variables and settings for integration.
•	References: Cite any sources, libraries, APIs, or documentation consulted during the project.
•	Curriculum Vitae. Use the format in capstone project.


Note: use the formatting you use in capstone project like pagination, bullets and numbering, paragraph and line spacing, margins, paper size, font face, and font size table and figure format.

