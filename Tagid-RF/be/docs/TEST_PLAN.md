# Tagid-RF Test Plan

This document outlines the testing strategy for the Tagid-RF system, focusing on software components (Auth, RBAC, Payments) independent of physical hardware availability.

## 1. Testing Strategy Overview

We employ a pyramid testing strategy:

- **Unit Tests**: Isolated tests for individual functions and classes.
- **Integration Tests**: Verification of interactions between modules (e.g., API -> DB, API -> Auth).
- **System/E2E Flows**: verification of complete business processes (Login -> Scan -> Pay).

## 2. Test Coverage Goals (Phase-by-Phase)

### Phase 1 & 2: Infrastructure & Reader Service (Completed)

- [x] **RFID Protocol Parsing**: Verify correct hex parsing and command serialization.
- [x] **Scan Buffering**: Verify that high-volume scans are buffered and flushed correctly to the DB.
  - *Test*: Simulating 200 rapid scans and checking DB row count.

### Phase 3: Hardware Integration (Paused)

- [ ] Manual validation when power is restored.

### Phase 4: Feature Implementation (RBAC & Logic)

This is the current focus area.

#### 4.1. Authentication & Authorization (RBAC)

**Objective**: Ensure strict separation of duties and secure access.

- **Unit Tests (`tests/unit/test_auth.py`)**:
  - Token generation validity check.
  - Password hashing and verification.
  - Google OAuth token verification (Mocked).

- **Integration Tests (`tests/integration/test_rbac_flow.py`)**:
  - **Heirarchy Limit**: Verify `STORE_MANAGER` cannot create `NETWORK_MANAGER`.
  - **Cross-Tenant Access**: Verify User A (Store X) cannot view data of User B (Store Y).
  - **Public Registration**: Ensure public users can only register as `CUSTOMER`.

#### 4.2. Payment Processing

**Objective**: Verify correct handling of amounts, status updates, and provider switching.

- **Unit Tests (`tests/unit/test_payment.py`)**:
  - Calculate payment math (taxes, discounts).
  - Verify payload construction for simulated providers (Mock Gateway).

- **Integration Tests (`tests/integration/test_payment_flow.py`)**:
  - **Happy Path**: Create Intent -> Confirm -> Verify DB Status = `COMPLETED`.
  - **Refunds**: Verify only `COMPLETED` payments can be refunded.
  - **Partial Refund**: Verify logic for partial amounts (if supported).
  - **Inventory Update**: Confirm stock decrement upon successful payment.

#### 4.3. Push Notifications & Alerts

**Objective**: Verify alerts are triggered and routed to the correct clients.

- **Alert Logic**: Verify theft detection logic triggers an event.
- **Delivery**: Verify WebSocket broadcast receives the alert payload.

## 3. Manual Testing Checklist (For User)

Since automated UI tests are evolving, use this checklist for manual validation:

### A. Login & Users

1. [ ] **Admin Login**: Login as `super_admin`, go to Users page.
2. [ ] **Create Manager**: Create a new user with `STORE_MANAGER` role.
3. [ ] **Manager Login**: Logout and login as the new Manager.
4. [ ] **Restricted Action**: Try to delete a Network Admin (should be hidden or fail).

### B. simulated Scanning & Cart

1. [ ] **Scan Loop**: Start scanning in `ScanPage` (using Mock Reader if offline).
2. [ ] **Add to Cart**: Verify scanned tags appear in the cart list.
3. [ ] **Pricing**: Check that total price updates correctly.

## 4. Execution Plan

1. Fix existing environment issues (path errors).
2. Run `pytest tests/integration/test_rbac_flow.py` to validate RBAC.
3. Develop `test_payment_flow.py`.
4. Report coverage and gaps.
