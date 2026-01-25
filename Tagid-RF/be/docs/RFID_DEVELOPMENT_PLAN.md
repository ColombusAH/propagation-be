# RFID Reader Development Plan

## Phase 1: Test Coverage & Stabilization (Completed)

- [x] Achieve >90% test coverage for `rfid_reader.py`.
- [x] Fix protocol parsing edge cases (unsolicited messages, partial packets).
- [x] Ensure robust error handling for network disconnections.

## Phase 2: Code Refactoring & Cleanup

- [ ] **Consolidate Tests**: Merge `test_rfid_reader_coverage_v3.py` and other temporary coverage files into a clean `tests/services/test_rfid_reader.py`.
- [ ] **Type Safety**: Add stricter type hints to `m200_protocol.py` and enforce them with `mypy`.
- [ ] **Logging**: Improve logging granularity (DEBUG for raw bytes, INFO for flow).

## Phase 3: Hardware Integration & Validation

- [ ] **Live Testing**: Connect to the physical M-200 reader and validate the "Happy Path" scenarios.
- [ ] **Latency Tuning**: Measure the latency of tag reads -> WebSocket broadcast. Optimize `_scan_loop` sleep times.
- [ ] **GPIO Testing**: Validate that setting GPIO/Relays actually triggers the physical ports.

## Phase 4: Feature Implementation

- [ ] **Tag Writing**: Implement the `write_tag` method in `rfid_reader.py` (currently returns False).
  - Needs `RFM_WRITE_TAG` (0x0004) command implementation in protocol.
- [ ] **Inventory Modes**: Expose different inventory modes (Single vs. Continuous) via the API.
- [ ] **Multi-Reader Support**: ensure `RFIDReaderService` can manage multiple reader instances if required.

## Phase 5: Frontend Integration (Next Steps)

- [ ] **WebSocket Client**: Updates the React `ScanPage` to handle `tag_scanned` mock events vs real events.
- [ ] **Dashboard**: Display RSSI signal strength visually.
- [ ] **Device Settings**: Create a UI page to call `set_power`, `set_network`, etc.

## Phase 6: Persistence

- [ ] **Configuration Storage**: Save reader settings (IP, Power, etc.) to the PostgreSQL database so they persist across restarts.
- [ ] **Scan History**: Ensure efficient storage of high-volume scan data (potentially buffering writes).
