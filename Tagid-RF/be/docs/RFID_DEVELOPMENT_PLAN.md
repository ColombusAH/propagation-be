# RFID Reader Development Plan

## Phase 1: Test Coverage & Stabilization (Completed)

- [x] Achieve >90% test coverage for `rfid_reader.py`.
- [x] Fix protocol parsing edge cases (unsolicited messages, partial packets).
- [x] Ensure robust error handling for network disconnections.

## Phase 2: Code Refactoring & Cleanup (Completed)

- [x] **Consolidate Tests**: Merge temporary coverage files into a clean `tests/services/test_rfid_reader.py`.
- [x] **Type Safety**: Add stricter type hints to `m200_protocol.py`.
- [x] **Logging**: Improve logging granularity (DEBUG for raw bytes, INFO for flow).

## Phase 3: Hardware Integration & Validation (PAUSED - No Power)

- [ ] **Live Testing**: Connect to the physical M-200 reader.
- [ ] **Latency Tuning**: Optimize `_scan_loop` sleep times.
- [ ] **GPIO Testing**: Validate relay/buzzer triggers.

## Phase 4: Feature Implementation

- [x] **Tag Writing**: Implement `write_tag` method in `rfid_reader.py`.
- [x] **Inventory Modes**: Expose Single vs. Continuous scan via API.
- [ ] **Multi-Reader Support**: Manage multiple reader instances.

## Phase 5: Frontend Integration (In Progress)

- [x] **WebSocket Client**: Real-time `tag_scanned` events in `ScanPage`.
- [x] **Visual RSSI**: Added gauge bars in `ScanPage`.
- [x] **Push UI**: Display theft/system alerts in the frontend UI.

## Phase 6: Persistence & Business Logic

- [x] **Configuration Storage**: Persistent reader settings (IP, Power, etc.) in DB.
- [x] **Scan History Optimization**: Buffer writes for high-volume scans.
- [x] **Payment Verification**: Validated payment creation, confirmation, and refund logic via integration tests.
- [x] **RBAC Flow**: Verified hierarchical permissions (Super Admin -> Store Manager -> Employee) and API protection.
- [ ] **Push Notifications**: Connect to real push service (Firebase/FCM) for theft alerts.

## Phase 7: Mock Catalog & Demo Environment (Immediate)

- [ ] **Demo Seed Script**: Create a script to populate the DB with a "Demo Store" (electronics/clothing).
- [ ] **Tag-Product Mapping**: Pre-assign specific RFID EPCs to demo products for consistent testing.
- [ ] **Virtual Inventory**: Setup mock inventory levels to demonstrate real-time stock updates during scans.

## Phase 8: Payment Gateway Expansions (Future)

- [ ] **Nayax Integration**: Implement terminal-based payment support for physical checkout kiosks.
- [ ] **Tranzila Support**: Add the Israeli payment gateway for local credit card processing.
- [ ] **Unified Payment Layer**: Refactor `payment_service` to allow seamless switching between Stripe, Nayax, and Tranzila.
