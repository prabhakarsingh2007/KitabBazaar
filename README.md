# KitabBazaar - E-Commerce Bookstore Platform

KitabBazaar is a premium, production-ready Django e-commerce platform designed for selling and managing books. It features a complete shopping experience with guest cart support, unique Unicode slugs, a customer profile order tracking dashboard, a robust admin dashboard with inventory/status management, delivery date scheduling, and an advanced coupon promotion engine.

---

## Technical Stack
- **Framework**: Django 6.x (Python 3.14+)
- **Styling**: Tailwind CSS (integrated via `crispy-tailwind` and `crispy-forms`)
- **Database**: SQLite3 (fully transactional, support for atomic blocks)
- **Static Assets**: CompressedManifestStaticFilesStorage (via `WhiteNoise` for efficient serving)
- **Authentication**: Native Django Auth system, customized login redirection (`next` parameters), and guest-to-user database merging.

---

## Core Features

### 1. Advanced Coupon & Promotion Engine
- **Flexible Discounts**: Supports both Flat rate discount amounts (e.g., ₹50.00 off) and Percentage-based discounts (e.g., 10% off).
- **Percentage Cap Limit**: Restricts maximum discount values for percentage-based coupons (e.g., 20% off, capped up to ₹200.00).
- **Minimum Order Requirement**: Restricts coupon applications to orders that meet a minimum subtotal value.
- **Global & Per-User Limits**: Implements usage limits globally (e.g., coupon can only be used 100 times total) and per-user (e.g., limit to 1 usage per customer).
- **First-Order Only**: Restricts application to customers placing their very first order.
- **Free Shipping Support**: Dynamically waives standard delivery fees.
- **Session-Database Merge**: Guest coupons stored in sessions automatically sync to the database cart upon user login.
- **Admin Statistics**: Tracks coupon metrics (times used and total discounts granted) directly inside the custom admin list panel.

### 2. Guest Shopping Cart & Account Integration
- **Persistent Sessions**: Allows non-logged-in guest users to add books to their cart, change quantities, apply coupons, and estimate shipping/taxes.
- **Split-Login Workflow**: Preserves the checkout route via `?next=` redirection when prompting guests to authenticate.
- **Automatic Merging**: On login, cart items and coupons stored in session variables are automatically merged into database records (`OrderItem` and `Order` models).

### 3. Customer Dashboard & Real-Time Tracking
- **Order Progress Stepper**: Shows progress statuses (`Ordered` -> `Processing` -> `Shipped` -> `Delivered`).
- **Profile Management**: Update first/last names and emails directly from the profile.
- **Order Invoice History**: View invoices, subtotal breakdowns, applied discounts, transaction details, and delivery date details.

### 4. Delivery Date Scheduling
- **Admin Scheduler**: Allows administrators to specify or update the scheduled delivery date using a date-picker interface.
- **Customer Visibility**: Displays scheduled delivery dates directly on the order invoice and dashboard history grid.

### 5. Catalog Search & Filtering
- **Unicode Slug URLs**: Full support for international characters (e.g., Hindi slugs like `/filter/अकेलापन/` or `/book-view/अकेलापन-1/`) resolving duplicate slugs with sequential numbering checks.
- **Search Engine**: Real-time matching on book title and direct auto-redirect on exact ISBN matches.

---

## Database Architecture
Key models defined in the `ecom` application:
- **`Book`**: Covers catalog details (title, description, price, discount_price, edition, isbn, stock, cover_image, author, genre).
- **`Author` / `Genere`**: Models catalog attributes using unique unicode slug strings.
- **`Address`**: Manages customer delivery details (line 1, line 2, city, state, postal code, phone).
- **`Coupon`**: Configures rules, limitations, and discounts.
- **`Payment`**: Finalized order transaction details (amount, payment_method, mode, transaction_id).
- **`Order`**: Combines payment details, addresses, coupons, delivery dates, and status codes.
- **`OrderItem`**: Joins order items, quantities, and integrity constraints.

---

## Getting Started

### 1. Prerequisites
- Python 3.10+ installed.
- Git.

### 2. Installation & Setup
1. Clone the repository and navigate to the project directory:
   ```bash
   cd ecommercebook
   ```
2. Activate the virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     .\server\Scripts\Activate.ps1
     ```
   - **Linux/macOS**:
     ```bash
     source server/bin/activate
     ```
3. Navigate to the Django application folder:
   ```bash
   cd bookshop
   ```
4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Start the local server:
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to `http://127.0.0.1:8000/`.

---

## Running Verification Checks
To verify configuration validity and test code formatting:
- **System Integrity check**:
  ```bash
  python manage.py check
  ```
- **Template compile validations**:
  Verify templates using the compile check script:
  ```bash
  python check_templates.py
  ```
