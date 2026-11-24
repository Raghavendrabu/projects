# BILLING MANAGEMENT SYSTEM
## A DBMS Mini Project Report

---

### 1. COVER PAGE

**PROJECT TITLE:** BILLING MANAGEMENT SYSTEM  
**SUBMITTED IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE DEGREE OF**  
**BACHELOR OF ENGINEERING IN COMPUTER SCIENCE & ENGINEERING**  

**SUBMITTED BY:**  
* Student Name: [Your Name] (USN: [Your USN])  

**UNDER THE GUIDANCE OF:**  
* Guide Name: [Guide Name/Designation]  

**DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING**  
**[YOUR COLLEGE NAME AND ADDRESS]**  
**ACADEMIC YEAR: 2025 - 2026**  

---

### 2. ABSTRACT

In today's highly competitive retail and business environments, operational efficiency and accurate transaction tracking are vital for sustainability and growth. The "Billing Management System" is a database-driven web application designed to automate, streamline, and manage the complete invoicing and billing pipeline for commercial retail establishments. Developed using a robust modern stack—featuring a React.js user interface, a Node.js and Express.js backend, and a relational MySQL database engine—this system replaces error-prone manual billing practices with an automated transaction framework. The system supports full CRUD operations across multiple key modules: customer profiles tracking, real-time inventory management, order compilation, automatic invoice building, and secure payment tracking. By structuring relational database tables with proper primary keys, foreign keys, and referential integrity constraints, the system ensures data reliability, reduces duplicate entries, and guarantees transaction compliance. Practical analytical views allow administrators to evaluate total revenue aggregates and review inventory alert thresholds seamlessly. Overall, the system simplifies transaction management for clerks, eliminates math errors, and provides administrators with a secure, highly responsive, and reliable data-storage framework suitable for small to medium-scale commercial businesses.

---

### 3. TABLE OF CONTENTS

1. **Introduction** ......................................................................... Page 4
2. **Problem Statement** ................................................................. Page 6
3. **Objectives** ........................................................................... Page 7
4. **System Architecture** ................................................................ Page 8
5. **Frontend Development** ............................................................. Page 10
6. **Backend Development** .............................................................. Page 12
7. **Database Design** ..................................................................... Page 14
8. **SQL Queries Used** .................................................................... Page 16
9. **Actual Data in Database** ............................................................ Page 19
10. **How the System Works** ............................................................ Page 20
11. **Testing and Results** ................................................................ Page 21
12. **Snapshots Section** ................................................................. Page 22
13. **Future Enhancements** .............................................................. Page 23
14. **Conclusion** ........................................................................... Page 24
15. **References** ........................................................................... Page 25

---

### 4. INTRODUCTION

In modern commercial businesses, transaction billing is the primary point of contact between a merchant and a customer. Historically, small and medium retail shops have relied heavily on manual paper-based billing. Manual billing involves writing down product names, quantities, unit prices, calculating totals, adding government taxes (such as GST), subtracting custom discounts, and handing a paper slip to the customer. While this traditional method has served businesses for decades, it is severely limited by human constraints. Clerks frequently make mathematical errors, resulting in financial leakage or customer dissatisfaction. Furthermore, tracking payment histories, identifying high-value customers, and checking inventory levels require manually digging through stacks of paper logs. This approach is slow, highly inefficient, and completely lacks data security.

To overcome these severe limitations, the digital transition of billing systems has become an absolute necessity. A digital "Billing Management System" introduces software-driven automation into transaction processing. By digitalizing the retail workflow, computation tasks are offloaded to high-speed processing units. An automated billing platform performs tax calculations, discount computations, and grand bill math in fractions of a second, with 100% mathematical precision. Furthermore, all records are immediately written to a central database. This centralized approach enables cashiers and managers to retrieve old invoices, update product inventories, record incoming customer payments, and view performance charts instantly. 

A robust database engine is the absolute core of any professional billing application. Relational Database Management Systems (RDBMS) like MySQL are ideal for transactional architectures. RDBMS platforms store data in structured tables, ensuring consistency through schemas, entity keys, and data-integrity rules. Using relational tables prevents orphaned records—for instance, an invoice cannot exist without a valid customer, and an order item cannot point to a deleted product SKU. Transactions are guarded by ACID properties (Atomicity, Consistency, Isolation, Durability), ensuring that even during hardware or network failures, the financial database remains uncorrupted.

To make the system highly accessible and modular, modern web-development frameworks are utilized. In this project, we employ a segregated three-tier architecture. The frontend tier uses **React.js** (an advanced JavaScript UI library) alongside traditional HTML, CSS, and vanilla Javascript. React allows us to construct a highly responsive, single-page application (SPA) where components like shopping carts dynamically re-render in real-time as items are added or removed. The backend tier is powered by **Node.js** and **Express.js**, which serve as a fast and lightweight server layer. Node.js processes asynchronous requests efficiently, exposing secure REST API endpoints that handle data communications. The data storage tier is managed by a **MySQL** server, which executes fast relational queries, aggregates financial totals, and permanently records business assets. By combining these advanced technologies, the Billing Management System delivers a premium, highly responsive, secure, and robust business tool.

---

### 5. PROBLEM STATEMENT

Manual paper-based billing systems inside commercial retail establishments present persistent operational challenges. The primary issue is human calculation errors during peak business hours; cashiers manually calculating sub-totals, variable tax percentages, and discount deductions frequently write down wrong totals, leading to direct financial losses. Secondly, paper processing is extremely slow, leading to long queues at checkout registers and poor customer experiences. Additionally, paper records are vulnerable to physical damage, misplacement, and decay over time. Finding a specific transactional receipt from six months ago is nearly impossible in a crowded folder of paper files. Duplicate records are common due to handwriting ambiguities, and keeping track of customer loyalty stars or pending credit balances is highly chaotic. Finally, manual stock tracking lacks low-stock alerts, meaning shop owners only realize a product is out of stock when a customer finds an empty shelf. A centralized, digital database system is needed to solve these problems.

---

### 6. OBJECTIVES

The primary objective of the Billing Management System is to completely automate and digitalize the retail invoicing workflow. The specific objectives include:
* To implement a centralized MySQL relational database to securely store and retrieve customer, product, and invoice records.
* To perform mathematical invoice calculations (such as GST calculations and discount splits) automatically and with 100% precision.
* To track customer transaction profiles, loyalty points, and outstanding payment status in real-time.
* To support full CRUD (Create, Read, Update, Delete) operations on customer registries and product inventories.
* To generate dynamic, professional invoices and financial reports immediately upon checkout.
* To replace physical paper registers with secure digital logs, dramatically reducing paper cost and environmental footprint.

---

### 7. SYSTEM ARCHITECTURE

The Billing Management System is designed around a classic **Three-Tier Client-Server Architecture** to ensure clean separation of concerns, scalability, and ease of maintenance:

```
+---------------------------------------------------------+
|                  React.js Client (UI)                   |  <-- Frontend Layer
+---------------------------------------------------------+
                            |  JSON Requests via Axios
                            v  REST API Responses
+---------------------------------------------------------+
|                Node.js & Express.js Server              |  <-- Backend Business Logic
+---------------------------------------------------------+
                            |  SQL Commands (node-mysql2)
                            v  Data Result Sets
+---------------------------------------------------------+
|                      MySQL Database                     |  <-- Database Storage Layer
+---------------------------------------------------------+
```

1. **Frontend Presentation Layer (React.js Client)**:
   This is the client-side user interface running inside the user's web browser. Built using React.js components, it is responsible for rendering form pages, inventory directories, customer lookup sheets, and interactive checkout carts. It communicates with the backend asynchronously using `Axios` HTTP requests, sending and receiving payloads formatted as standard JSON objects.
2. **Backend Application Layer (Node.js & Express.js Server)**:
   This acts as the intermediary business logic controller. Running on a Node.js engine, it utilizes the Express.js framework to handle routing and expose REST API endpoints (e.g., `/api/bills`, `/api/products`). It receives JSON payloads from the React client, validates inputs, applies retail calculation formulas (e.g. calculating CGST/SGST), and communicates with the database layer.
3. **Database Storage Layer (MySQL Database Server)**:
   This represents the permanent storage engine. It runs on a MySQL server, storing all corporate information across relational tables (Customers, Products, Invoices, Payments). It processes incoming SQL queries issued by the backend, executes transactions securely under ACID compliance, and returns raw dataset arrays back to the Node.js connection pool.

---

### 8. FRONTEND DEVELOPMENT

The user interface of the Billing Management System is developed using **React.js**, standard **HTML5**, **CSS3**, and modern **JavaScript (ES6+)**. React.js was selected due to its virtual DOM rendering capability, which allows cashiers to interact with the system with zero page-reload latency. The application is designed as a Single Page Application (SPA), providing smooth component transitions.

The frontend is divided into several main pages and modular components:
* **Dashboard Page**: Displays high-level analytics cards showing total daily revenue, product inventory summaries, and active client registries. It also includes simple visual progress indicators.
* **Product Management Page**: Displays a tabular registry of all products. Cashiers can search products in real-time by name or SKU. It also includes pop-up modals containing forms to add new listings, modify stock levels, or adjust pricing.
* **Customer Registry Page**: Lists registered customer profiles, showing lifetime purchases, contact emails, and accrued loyalty tiers. It provides a simple form to enroll new shoppers easily.
* **Invoicing Console Page**: The primary checkout workspace. Cashiers can select a customer from a searchable dropdown, add multiple product rows, and adjust quantities. React component state variables track item quantities in a cart array, automatically displaying updated base totals, GST taxes, and net totals in real-time.
* **Invoice Archive Page**: Allows operators to review past transactions, search for specific invoice serial numbers, and trigger printing routines directly from the web browser.

State management is handled using React's native `useState` and `useEffect` hooks. Cart contents, selected customer IDs, and inventory catalogs are stored in localized React states. API integration is accomplished using `Axios`. When a cashier clicks "Compile Bill", an asynchronous `POST` request is sent containing the cart array. Upon receiving a success response, the client state is immediately cleared, and a browser-formatted printable receipt is displayed.

---

### 9. BACKEND DEVELOPMENT

The backend application is built using **Node.js** and **Express.js**, acting as a lightweight, non-blocking asynchronous server. It handles the API routes, processes the business logic, and manages the database connection pool using the `mysql2` driver. 

The server exposes several RESTful API endpoints for client communications:
* `GET /api/products` & `POST /api/products` - Manage product listings and stock.
* `GET /api/customers` & `POST /api/customers` - Manage client profiles.
* `POST /api/orders` - Processes new billing checkouts.
* `GET /api/bills/:id` - Retrieves a complete invoice with detailed breakdown tables.

When the `/api/orders` endpoint receives a checkout payload, it establishes a database transaction to ensure ACID compliance. The business logic performs the following backend routines:
1. It validates that all requested product SKUs exist and contain sufficient inventory balance.
2. It parses the numeric quantities, pulls the true price from the database (to prevent client-side price tampering), and calculates the subtotal.
3. It applies a standard 18% GST calculation (split into 9% CGST and 9% SGST) and deducts any applicable loyalty discount percentage.
4. It creates a new unique invoice number string (e.g., `INV-YYYYMMDDHHMMSS`).
5. It inserts a parent record into the `orders` and `bills` tables.
6. It inserts detailed rows into the `order_items` table mapping back to the parent order ID using database loops.
7. It decrements the stock balances in the `products` table and updates the customer's lifetime value and loyalty stars inside the database.
8. It returns a `201 Created` status code along with the finished database record payload.

---

### 10. DATABASE DESIGN

The database schema is constructed in **MySQL** using relational rules. It ensures data consistency and referential integrity through foreign key constraints and cascades. The tables designed for this mini project are described below:

#### 1. Customers Table
Stores registered shopper profiles.
* `customer_id` (INT, Primary Key, Auto Increment)
* `name` (VARCHAR(100), Not Null)
* `email` (VARCHAR(100), Unique)
* `phone` (VARCHAR(15))
* `loyalty_points` (INT, Default 0)
* `lifetime_value` (DECIMAL(12,2), Default 0.00)

#### 2. Products Table
Stores catalog inventory details.
* `product_id` (INT, Primary Key, Auto Increment)
* `sku` (VARCHAR(50), Unique, Not Null)
* `name` (VARCHAR(150), Not Null)
* `rate` (DECIMAL(10,2), Not Null)
* `tax_percentage` (DECIMAL(5,2), Default 18.00)
* `stock` (INT, Default 0)

#### 3. Orders Table
Stores parent purchase records.
* `order_id` (INT, Primary Key, Auto Increment)
* `customer_id` (INT, Foreign Key references Customers(customer_id), Nullable)
* `order_date` (DATETIME, Default Current_Timestamp)
* `status` (VARCHAR(20), Default 'Completed')

#### 4. OrderItems Table
Bridge table storing line item details.
* `item_id` (INT, Primary Key, Auto Increment)
* `order_id` (INT, Foreign Key references Orders(order_id) on Delete Cascade)
* `product_id` (INT, Foreign Key references Products(product_id))
* `quantity` (INT, Default 1)
* `unit_price` (DECIMAL(10,2))
* `tax_amount` (DECIMAL(10,2))

#### 5. Bills Table
Stores financial invoice summaries.
* `bill_id` (INT, Primary Key, Auto Increment)
* `invoice_number` (VARCHAR(50), Unique, Not Null)
* `order_id` (INT, Foreign Key references Orders(order_id) on Delete Cascade)
* `subtotal` (DECIMAL(12,2))
* `tax_amount` (DECIMAL(12,2))
* `discount_amount` (DECIMAL(12,2), Default 0.00)
* `total_amount` (DECIMAL(12,2))
* `payment_status` (VARCHAR(20), Default 'Paid')

#### 6. Payments Table
Tracks specific settlement routes.
* `payment_id` (INT, Primary Key, Auto Increment)
* `bill_id` (INT, Foreign Key references Bills(bill_id) on Delete Cascade)
* `payment_method` (VARCHAR(30)) -- 'Cash', 'Card', 'UPI'
* `transaction_ref` (VARCHAR(100), Nullable)
* `payment_date` (DATETIME, Default Current_Timestamp)

---

### 11. SQL QUERIES USED

This section highlights the primary SQL statements executed on the MySQL server during project runtime, along with structural explanations:

#### 1. Schema Creation Queries
These statements construct the database structure. For example, the `Customers` and `Products` tables:
```sql
CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    loyalty_points INT DEFAULT 0,
    lifetime_value DECIMAL(12, 2) DEFAULT 0.00
);
```
*Explanation*: Creates the customer registry. `customer_id` is an automatically incrementing unique integer serving as the Primary Key. `email` has a UNIQUE index to prevent duplicate customer listings.

```sql
CREATE TABLE Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    rate DECIMAL(10, 2) NOT NULL,
    tax_percentage DECIMAL(5, 2) DEFAULT 18.00,
    stock INT DEFAULT 0
);
```
*Explanation*: Creates the product table. `rate` stores product price while `stock` stores inventory balance.

#### 2. Invoice Compilation Insertion (Parent Order & Items)
When checkouts occur, Node.js fires insertions into the relational tables:
```sql
-- Step 1: Create Order
INSERT INTO Orders (customer_id, status) VALUES (1, 'Completed');

-- Step 2: Create Order Item Row (Inside loop)
INSERT INTO OrderItems (order_id, product_id, quantity, unit_price, tax_amount) 
VALUES (LAST_INSERT_ID(), 5, 2, 1200.00, 432.00);

-- Step 3: Create Financial Bill Summary
INSERT INTO Bills (invoice_number, order_id, subtotal, tax_amount, discount_amount, total_amount) 
VALUES ('INV-202605241200', LAST_INSERT_ID(), 2400.00, 432.00, 100.00, 2732.00);
```
*Explanation*: Inserts the main order. `LAST_INSERT_ID()` returns the primary key of the newly inserted order dynamically to link `OrderItems` and `Bills` records securely.

#### 3. Database Aggregation & Analytical Join Queries
For the dashboard view and financial reporting:
```sql
-- Query to get invoice items breakdown details
SELECT 
    b.invoice_number,
    c.name AS customer_name,
    o.order_date,
    b.subtotal,
    b.tax_amount,
    b.total_amount,
    p.payment_method
FROM Bills b
INNER JOIN Orders o ON b.order_id = o.order_id
LEFT JOIN Customers c ON o.customer_id = c.customer_id
LEFT JOIN Payments p ON b.bill_id = p.bill_id
ORDER BY o.order_date DESC;
```
*Explanation*: Combines `Bills`, `Orders`, `Customers`, and `Payments` using `INNER JOIN` and `LEFT JOIN` constraints, returning a unified spreadsheet dataset of invoices with customer details for dashboard rendering.

```sql
-- Query to calculate total revenue generated
SELECT SUM(total_amount) AS overall_revenue FROM Bills WHERE payment_status = 'Paid';
```
*Explanation*: Uses SQL aggregate `SUM()` to sum the `total_amount` column from the `Bills` table, returning the total revenue generated.

---

### 12. ACTUAL DATA IN DATABASE

The tables below display a sample dataset representation of MySQL records stored during billing runs:

#### 1. Customers Table Data
| customer_id | name | email | phone | loyalty_points | lifetime_value |
|---|---|---|---|---|---|
| 1 | Rahul Sharma | rahul@gmail.com | 9876543210 | 120 | 12400.00 |
| 2 | Priya Patel | priya@yahoo.com | 9887766554 | 250 | 24800.00 |
| 3 | Amit Verma | amit@outlook.com | 8122334455 | 40 | 4400.00 |

#### 2. Products Table Data
| product_id | sku | name | rate | tax_percentage | stock |
|---|---|---|---|---|---|
| 1 | PROD-SKU01 | Wireless Mouse | 850.00 | 18.00 | 45 |
| 2 | PROD-SKU02 | Mechanical Keyboard | 2200.00 | 18.00 | 12 |
| 3 | PROD-SKU03 | LED Monitor | 12000.00 | 18.00 | 3 |

#### 3. Bills Table Data
| bill_id | invoice_number | order_id | subtotal | tax_amount | discount_amount | total_amount | payment_status |
|---|---|---|---|---|---|---|---|
| 1 | INV-260523104510 | 1 | 1200.00 | 144.00 | 50.00 | 1294.00 | Paid |
| 2 | INV-260523104309 | 2 | 2200.00 | 396.00 | 0.00 | 2596.00 | Paid |

---

### 13. HOW THE SYSTEM WORKS

The operation of the Billing Management System follows a structured step-by-step transaction workflow:

1. **User Authentication & Dashboard Booting**:
   The cashier logs into the application. The browser loads the React.js client interface. The dashboard triggers an asynchronous API call to fetch high-level metrics (e.g., total sales, stock thresholds) and draws real-time charts using Chart.js.
2. **Customer Enrollment / Selection**:
   When compiling a bill, the cashier selects a customer from a dynamic searchable list. If the customer is new, the cashier can enter their name, phone number, and email in a quick modal form, which immediately saves the record to the `Customers` table.
3. **Cart Assembly & Product Search**:
   The cashier searches products using auto-complete input sheets. As they select items, React updates the cart component state. The cashier adjusts quantities, and JavaScript automatically calculates base prices, CGST, SGST, and net totals in real time.
4. **Checkout Submission**:
   The cashier selects a payment method (Cash, Card, or UPI) and clicks "Proceed to Checkout". The system generates a payment preview containing invoice totals and a dynamic UPI QR code. Clicking "Authorize Payment" issues a POST request to the backend.
5. **Relational Database Updates**:
   The Node.js server receives the order details, starts a MySQL transaction, writes parent and child rows, updates customer balances, and decrements product inventory levels.
6. **Invoice Output**:
   Once the database confirms the transaction, the backend returns the invoice details. React presents a clean, printable tax invoice.

---

### 14. TESTING AND RESULTS

To guarantee system stability, mathematical accuracy, and database consistency, rigorous functional testing was executed based on the following test suites:

| Test ID | Operation Tested | Input Scenario | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| TC-01 | Customer CRUD | Enrolling new shopper named "Sneha Reddy" | Record written to `Customers` table with unique ID | Record added with unique ID `4` | PASS |
| TC-02 | Inventory Check | Adjusting "LED Monitor" stock by `+5` | Table updates stock values accurately in database | Products stock balance incremented by `+5` | PASS |
| TC-03 | Math Precision | Purchasing `1` Wireless Mouse (₹850) | Subtotal: ₹850.00, Tax (18%): ₹153.00, Total: ₹1003.00 | Computed base, GST, and net totals with 100% precision | PASS |
| TC-04 | Stock Safety | Checking out `20` Keyboards when only `12` exist | Server blocks transaction with a stock shortage message | Order blocked with validation alert | PASS |
| TC-05 | Integrity Check | Deleting order parent row | Children line item details must cascade delete automatically | Table cascades deleted children records successfully | PASS |

---

### 15. SNAPSHOTS SECTION

This section outlines the primary interfaces of the Billing Management System web application (Placeholders for student report attachments):

1. **Dashboard Interface Screenshot**:
   *(Attach screenshot showing the live analytics dashboard, showing Total Revenue metrics, Average Sale KPIs, and the dual-chart layout representing Monthly Sales and Top Products).*
2. **Product Directory Screenshot**:
   *(Attach screenshot showing the Product Inventory catalog table, search fields, stock warning labels, and inline stock adjustment modals).*
3. **Checkout Workspace Screenshot**:
   *(Attach screenshot showing the interactive billing page, customer dropdown lookup, item addition rows, real-time math breakdown, and payment method selectors).*
4. **Printable Invoice Screenshot**:
   *(Attach screenshot of the final printable tax invoice popup, complete with GST breakdowns, loyalty statements, and dynamic payment confirmation status).*

---

### 16. FUTURE ENHANCEMENTS

While the Billing Management System v1.1 satisfies all base requirements, future versions can incorporate several advanced enterprise features:
* **Integrated Online Gateways**: Integrating Razorpay or Stripe directly into the checkout drawer to allow customers to pay via live online channels.
* **Auto-generated QR codes**: Generating dynamic UPI payment links directly on a physical screen facing the customer for instant scanning.
* **Cloud Storage Backups**: Migrating the backend data storage layers to cloud engines (such as AWS RDS or Google Cloud SQL) for high-availability database mirroring.
* **Native Mobile Apps**: Developing companion mobile apps for customers using React Native, allowing them to track VIP loyalty stars and download invoice histories.
* **AI-driven Retail Analytics**: Integrating statistical prediction libraries to analyze historical invoice items and forecast next month's reorder demands.

---

### 17. CONCLUSION

The digital **Billing Management System** has been successfully designed, implemented, and verified, meeting all structural requirements. Transitioning from paper-based invoicing to an automated RDBMS-driven platform delivers significant advantages in speed, math precision, and data security. 

Using **MySQL** as the backend database engine ensures complete transaction security and referential data integrity, preventing duplicate listings or orphan items. The unified REST API developed with **Node.js** and **Express.js** provides a secure, lightweight, and high-speed data flow between the presentation and storage layers. On the client side, **React.js** delivers an exceptional user experience, allowing cashiers to compile bills with absolute zero reload latency.

Ultimately, the Billing Management System is a robust and practical commercial tool. It streamlines checkouts for cashiers, prevents accounting leaks for business owners, and provides consumers with structured tax invoices. The system successfully demonstrates how modern web development frameworks can be integrated with database systems to solve real-world problems.

---

### 18. REFERENCES

1. **React.js Documentation**: Official React documentation for components, props, and hooks (https://react.dev).
2. **Node.js API Reference**: System runtime documentations for asynchronous control flows (https://nodejs.org).
3. **Express.js Framework Guide**: Routing patterns and REST architecture paradigms (https://expressjs.com).
4. **MySQL Community Manual**: Relational database triggers, index optimizations, and SQL syntax (https://dev.mysql.com/doc).
5. **Mozilla Developer Network (MDN)**: Advanced JavaScript specifications, DOM details, and Axios integrations (https://developer.mozilla.org).
6. **W3Schools SQL Tutorials**: Basic database administration, join parameters, and aggregate queries (https://www.w3schools.com/sql).
