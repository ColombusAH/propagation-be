---
id: encryption-payment-implementation-plan
name: Encryption & Payment Implementation Plan
description: Improve backend test coverage to 90% and finalize payment/encryption logic.
task_id: backend-test-coverage
status: proposed
---

## Current Status

- Backend coverage is around 41%.
- Major gaps in `rfid_reader.py`, `m200_protocol.py`, `inventory.py`, `cash_provider.py`, `nexi_provider.py`.
- `inventory.py` tests are written but failing due to mocking issues.
- `cash_provider` and `nexi_provider` tests are written but need verification.

## User Review Required
>
> [!IMPORTANT]
>
> - Confirm priority of `rfid_reader.py` mocking (it is complex hardware interaction).
> - Approve the strategy of mocking `prisma_client` at the service import level.

## Proposed Changes

### 1. Fix Inventory Service Tests

- **File**: `be/tests/services/test_inventory_service_mock.py`
- **Issue**: `AsyncMock` vs `MagicMock` return values causing assertions to fail (e.g., `snapshot.id` being a mock object instead of string).
- **Fix**: Ensure `MockModel` and return values are properly configured for `AsyncMock`.
- **Validation**: Pass all tests in `test_inventory_service_mock.py`.

### 2. Verify Payment Provider Tests

- **Files**: `be/tests/services/test_cash_provider_mock.py`, `be/tests/services/test_nexi_provider_mock.py`
- **Action**: Run these specific tests and fix any import/async issues.
- **Validation**: 100% pass rate for payment providers.

### 3. Implement RFID Reader & Protocol Mocks

- **target**: `be/app/services/rfid_reader.py` (Currently 11%)
- **Strategy**:
  - Create `be/tests/services/test_rfid_reader_mock.py`.
  - Mock internal socket/serial communication.
  - Test command sending and response parsing logic without actual hardware.
- **Validation**: Increase `rfid_reader` coverage > 80%.

### 4. Final Coverage Run

- **Action**: Run `pytest --cov=app`
- **Goal**: > 90% total coverage.

## Verification Plan

1. Run `python -m pytest be/tests/services/test_inventory_service_mock.py` -> PASS.
2. Run `python -m pytest be/tests/services/test_cash_provider_mock.py` -> PASS.
3. Run `python -m pytest be/tests/services/test_nexi_provider_mock.py` -> PASS.
4. Run `python -m pytest be/tests/services/test_rfid_reader_mock.py` -> PASS.
5. Generate Coverage Report.
