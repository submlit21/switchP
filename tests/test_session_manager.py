"""Tests for thread-safe session manager."""

import pytest
from unittest.mock import Mock, patch
import threading
import time

from session.manager import SessionManager, Session


class TestSessionManager:
    """Tests for SessionManager class."""

    def test_create_session_returns_session(self):
        """Test that create_session creates a session for a client."""
        manager = SessionManager()
        session = manager.create_session("client1")
        assert isinstance(session, Session)
        assert hasattr(session, "connection")
        assert hasattr(session, "state")
        assert hasattr(session, "username")
        assert hasattr(session, "password")
        assert hasattr(session, "prompt_detector")
        assert hasattr(session, "logger")
        assert manager.get_session("client1") is session

    def test_get_session_raises_for_nonexistent_client(self):
        """Test that get_session raises KeyError for unknown client."""
        manager = SessionManager()
        with pytest.raises(KeyError):
            manager.get_session("unknown")

    def test_close_session_removes_session(self):
        """Test that close_session removes the session."""
        manager = SessionManager()
        manager.create_session("client1")
        assert manager.get_session("client1") is not None
        manager.close_session("client1")
        with pytest.raises(KeyError):
            manager.get_session("client1")

    def test_session_isolation(self):
        """Test that sessions are isolated per client."""
        manager = SessionManager()
        session1 = manager.create_session("client1")
        session2 = manager.create_session("client2")
        assert session1 is not session2
        assert manager.get_session("client1") is session1
        assert manager.get_session("client2") is session2

    def test_thread_safety_create_session(self):
        """Test that concurrent create_session calls are thread-safe."""
        manager = SessionManager()
        results = []
        errors = []

        def create(client_id):
            try:
                session = manager.create_session(client_id)
                results.append((client_id, session))
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(10):
            t = threading.Thread(target=create, args=(f"client{i}",))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        client_ids = {cid for cid, _ in results}
        assert len(client_ids) == 10
        for client_id, session in results:
            assert manager.get_session(client_id) is session

    def test_per_session_locking_queues_commands(self):
        """Test that commands for same session are queued and executed sequentially."""
        manager = SessionManager()
        session = manager.create_session("client1")
        execution_order = []
        lock_held = threading.Event()
        proceed = threading.Event()

        def command1(sess):
            execution_order.append(1)
            lock_held.set()
            proceed.wait()
            return "result1"

        def command2(sess):
            execution_order.append(2)
            return "result2"

        t1 = threading.Thread(
            target=lambda: manager.with_session_lock("client1", command1)
        )
        t1.start()
        lock_held.wait()
        t2 = threading.Thread(
            target=lambda: manager.with_session_lock("client1", command2)
        )
        t2.start()
        time.sleep(0.01)
        assert 2 not in execution_order
        proceed.set()
        t1.join()
        t2.join()
        assert execution_order == [1, 2]

    def test_with_session_lock_returns_result(self):
        """Test that with_session_lock passes session to function and returns result."""
        manager = SessionManager()
        manager.create_session("client1")

        def add_cred(sess):
            sess.username = "user"
            sess.password = "pass"
            return "ok"

        result = manager.with_session_lock("client1", add_cred)
        assert result == "ok"
        session = manager.get_session("client1")
        assert session.username == "user"
        assert session.password == "pass"

    def test_with_session_lock_propagates_exception(self):
        """Test that exceptions from function are propagated."""
        manager = SessionManager()
        manager.create_session("client1")

        def raise_error(sess):
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            manager.with_session_lock("client1", raise_error)
