"""
Coverage tests for TagStore class.
"""

import time

import pytest
from app.services.tag_store import TagStore


class TestTagStoreCoverage:

    def test_tag_store_functionality(self):
        store = TagStore()

        # Test add_tag
        store.add_tag({"epc": "E1", "rssi": -60})
        assert "E1" in store.tags
        assert store.tags["E1"]["rssi"] == -60

        # Test update existing
        store.add_tag({"epc": "E1", "rssi": -50})
        assert store.tags["E1"]["rssi"] == -50

        # Test get_recent (all valid)
        recent = store.get_recent(10)
        assert len(recent) == 1
        assert recent[0]["epc"] == "E1"

        # Test expiration cleanup
        # Manually backdate a tag
        store.tags["OLD"] = {"epc": "OLD", "timestamp": time.time() - 100}

        # cleanup defaults to 60s?
        # Check source code default if possible, or just assume logic works
        # TagStore.cleanup()
        store.cleanup(ttl=10)  # 10s TTL

        assert "OLD" not in store.tags
        assert "E1" in store.tags  # E1 was just added

    def test_tag_store_clear(self):
        store = TagStore()
        store.add_tag({"epc": "E1"})
        store.clear()
        assert len(store.tags) == 0
