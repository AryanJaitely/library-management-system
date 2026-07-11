# Library Management System – Backend API

A RESTful backend application for managing a library's daily operations, including book inventory, student records, borrowing and return workflows, authentication, and automated fine calculation.

Built using **FastAPI**, **SQLAlchemy**, and **MySQL**, the project follows a modular architecture with separate layers for routing, business logic, database models, and validation.

---

## Overview

The Library Management System provides a complete backend solution for handling library operations through REST APIs.

It supports secure librarian authentication, CRUD operations for books, authors, categories, and students, along with an automated borrowing workflow that tracks issued books, calculates overdue fines, and generates useful library reports.

The project emphasizes clean architecture, scalable API design, and database-driven application development using modern Python technologies.

---

## Features

- JWT-based authentication and authorization
- Book inventory management
- Author and category management
- Student record management
- Book issue and return workflow
- Automatic overdue detection
- Fine calculation based on overdue duration
- Book search and filtering
- Library statistics and reporting
- Modular REST API architecture

---

## System Workflow

```
Librarian Authentication
          │
          ▼
Book / Student Management
          │
          ▼
Issue Book
          │
          ▼
Track Due Date
          │
          ▼
Return Book
          │
          ▼
Fine Calculation
          │
          ▼
Reports & Statistics
```

---

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- MySQL
- Alembic
- Pydantic
- JWT Authentication
- Passlib (bcrypt)
- Uvicorn

---

## Authentication

The application uses **JWT (JSON Web Tokens)** for securing protected endpoints.

Librarians can:

- Register an account
- Log in to obtain an access token
- Access protected endpoints using a Bearer token

---

## Core Functionalities

### Book Management

- Add, update, delete, and search books
- Filter books by title, ISBN, author, category, and availability
- Track available copies

### Student Management

- Maintain student records
- Update and remove student information
- Track borrowing history

### Book Transactions

- Issue books to students
- Return books
- Prevent duplicate active loans
- Prevent issuing unavailable books
- Automatically detect overdue books

### Fine Management

The system automatically calculates overdue fines based on configurable business rules.

Fine amount is determined using:

```
Fine = Days Overdue × Fine Per Day
```

### Reports

The API provides endpoints for:

- Library statistics
- Most borrowed books
- Outstanding student fines

---

## Business Rules

- Books cannot be issued when no copies are available.
- A student cannot borrow the same book more than once while an active loan exists.
- Overdue books automatically accumulate fines.
- Books, authors, and categories cannot be removed while referenced by active records.
- Protected operations require authentication.

---

## Future Improvements

- Email reminders for overdue books
- Reservation and waitlist system
- Barcode/QR code integration
- Role-based access control
- Docker deployment
- Unit and integration testing
- CI/CD pipeline
