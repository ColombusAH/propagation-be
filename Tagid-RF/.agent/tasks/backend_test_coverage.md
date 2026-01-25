---
id: backend-test-coverage
name: Backend Test Coverage Improvement
description: Increase backend test coverage to 90% by adding mock-based tests for low-coverage services (`inventory.py`, `rfid_reader.py`, `cash_provider.py`, `nexi_provider.py`) and fixing existing failing tests.
status: proper
---

- [ ] **Fix Inventory Service Tests**: Debug and resolve failures in `test_inventory_service_mock.py` to ensure `inventory.py` is properly tested. <!-- id: 0 -->
- [ ] **Add Cash Provider Tests**: Verify `test_cash_provider_mock.py` passes and covers `cash_provider.py`. <!-- id: 1 -->
- [ ] **Add Nexi Provider Tests**: Verify `test_nexi_provider_mock.py` passes and covers `nexi_provider.py`. <!-- id: 2 -->
- [ ] **Improve RFID Reader Coverage**: Create mock tests for `rfid_reader.py` and `m200_protocol.py` to address the largest coverage gaps. <!-- id: 3 -->
- [ ] **Verify Total Coverage**: Run full suite with coverage report to confirm 90% target is met. <!-- id: 4 -->
