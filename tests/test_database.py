# """
# Unit tests for ChatDatabase
# Tests database operations using in-memory SQLite
# """

# import pytest
# import os
# from database import ChatDatabase


# class TestChatDatabase:
#     """Test suite for ChatDatabase class"""
    
#     @pytest.fixture
#     def db(self, tmp_path):
#         """Create a temporary test database"""
#         db_path = tmp_path / "test_chat.db"
#         return ChatDatabase(db_name=str(db_path))
    
#     def test_create_table(self, db):
#         """Test that table is created successfully"""
#         conn = db.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
#         result = cursor.fetchone()
#         conn.close()
        
#         assert result is not None
#         assert result[0] == 'chat_history'
    
#     def test_insert_message(self, db):
#         """Test inserting a message"""
#         db.insert_message(
#             session_id="test_session_001",
#             user_query="What's the weather?",
#             ai_response="It's sunny.",
#             intent="weather",
#             pdf_name=None
#         )
        
#         history = db.get_session_history("test_session_001")
        
#         assert len(history) == 2  # User + AI message
#         assert history[0]["role"] == "human"
#         assert history[0]["content"] == "What's the weather?"
#         assert history[1]["role"] == "ai"
#         assert history[1]["content"] == "It's sunny."
    
#     def test_get_session_history(self, db):
#         """Test retrieving session history"""
#         # Insert multiple messages
#         db.insert_message("session_001", "Question 1", "Answer 1", "document", "test.pdf")
#         db.insert_message("session_001", "Question 2", "Answer 2", "weather", None)
        
#         history = db.get_session_history("session_001")
        
#         assert len(history) == 4  # 2 user + 2 AI messages
#         assert history[0]["content"] == "Question 1"
#         assert history[1]["content"] == "Answer 1"
#         assert history[2]["content"] == "Question 2"
#         assert history[3]["content"] == "Answer 2"
    
#     def test_get_session_pdf(self, db):
#         """Test retrieving PDF name for a session"""
#         db.insert_message("session_001", "Query", "Answer", "document", "sample.pdf")
        
#         pdf_name = db.get_session_pdf("session_001")
        
#         assert pdf_name == "sample.pdf"
    
#     def test_get_session_pdf_no_pdf(self, db):
#         """Test retrieving PDF when none was used"""
#         db.insert_message("session_001", "Query", "Answer", "weather", None)
        
#         pdf_name = db.get_session_pdf("session_001")
        
#         assert pdf_name is None
    
#     def test_get_all_sessions(self, db):
#         """Test getting all sessions"""
#         db.insert_message("session_001", "Q1", "A1", "weather")
#         db.insert_message("session_002", "Q2", "A2", "document", "test.pdf")
#         db.insert_message("session_001", "Q3", "A3", "weather")
        
#         sessions = db.get_all_sessions()
        
#         assert len(sessions) == 2
#         # Should be ordered by last_message DESC
#         assert sessions[0]["session_id"] == "session_001"
#         assert sessions[0]["message_count"] == 2
#         assert sessions[1]["session_id"] == "session_002"
#         assert sessions[1]["message_count"] == 1
    
#     def test_clear_session(self, db):
#         """Test clearing a specific session"""
#         db.insert_message("session_001", "Q1", "A1", "weather")
#         db.insert_message("session_002", "Q2", "A2", "weather")
        
#         db.clear_session("session_001")
        
#         history1 = db.get_session_history("session_001")
#         history2 = db.get_session_history("session_002")
        
#         assert len(history1) == 0
#         assert len(history2) == 2
    
#     def test_clear_all(self, db):
#         """Test clearing all sessions"""
#         db.insert_message("session_001", "Q1", "A1", "weather")
#         db.insert_message("session_002", "Q2", "A2", "weather")
        
#         db.clear_all()
        
#         sessions = db.get_all_sessions()
        
#         assert len(sessions) == 0


# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])

"""
Unit tests for ChatDatabase
Tests database operations using in-memory SQLite
"""

import pytest
import os
import time 
from database import ChatDatabase


class TestChatDatabase:
    """Test suite for ChatDatabase class"""
    
    @pytest.fixture
    def db(self, tmp_path):
        """Create a temporary test database"""
        db_path = tmp_path / "test_chat.db"
        return ChatDatabase(db_name=str(db_path))
    
    def test_create_table(self, db):
        """Test that table is created successfully"""
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'chat_history'
    
    def test_insert_message(self, db):
        """Test inserting a message"""
        db.insert_message(
            session_id="test_session_001",
            user_query="What's the weather?",
            ai_response="It's sunny.",
            intent="weather",
            pdf_name=None
        )
        
        history = db.get_session_history("test_session_001")
        
        assert len(history) == 2  # User + AI message
        assert history[0]["role"] == "human"
        assert history[0]["content"] == "What's the weather?"
        assert history[1]["role"] == "ai"
        assert history[1]["content"] == "It's sunny."
    
    def test_get_session_history(self, db):
        """Test retrieving session history"""
        # Insert multiple messages
        db.insert_message("session_001", "Question 1", "Answer 1", "document", "test.pdf")
        db.insert_message("session_001", "Question 2", "Answer 2", "weather", None)
        
        history = db.get_session_history("session_001")
        
        assert len(history) == 4  # 2 user + 2 AI messages
        assert history[0]["content"] == "Question 1"
        assert history[1]["content"] == "Answer 1"
        assert history[2]["content"] == "Question 2"
        assert history[3]["content"] == "Answer 2"
    
    def test_get_session_pdf(self, db):
        """Test retrieving PDF name for a session"""
        db.insert_message("session_001", "Query", "Answer", "document", "sample.pdf")
        
        pdf_name = db.get_session_pdf("session_001")
        
        assert pdf_name == "sample.pdf"
    
    def test_get_session_pdf_no_pdf(self, db):
        """Test retrieving PDF when none was used"""
        db.insert_message("session_001", "Query", "Answer", "weather", None)
        
        pdf_name = db.get_session_pdf("session_001")
        
        assert pdf_name is None
    
    def test_get_all_sessions(self, db):
        """Test getting all sessions"""
        db.insert_message("session_001", "Q1", "A1", "weather")
        time.sleep(0.01)  # <--- ADD A SMALL PAUSE
        db.insert_message("session_002", "Q2", "A2", "document", "test.pdf")
        time.sleep(0.01)  # <--- ADD A SMALL PAUSE
        db.insert_message("session_001", "Q3", "A3", "weather")
        
        sessions = db.get_all_sessions()
        
        assert len(sessions) == 2
        # Should be ordered by last_message DESC
        assert sessions[0]["session_id"] == "session_001" # This will now pass
        assert sessions[0]["message_count"] == 2
        assert sessions[1]["session_id"] == "session_002"
        assert sessions[1]["message_count"] == 1
    
    def test_clear_session(self, db):
        """Test clearing a specific session"""
        db.insert_message("session_001", "Q1", "A1", "weather")
        db.insert_message("session_002", "Q2", "A2", "weather")
        
        db.clear_session("session_001")
        
        history1 = db.get_session_history("session_001")
        history2 = db.get_session_history("session_002")
        
        assert len(history1) == 0
        assert len(history2) == 2
    
    def test_clear_all(self, db):
        """Test clearing all sessions"""
        db.insert_message("session_001", "Q1", "A1", "weather")
        db.insert_message("session_002", "Q2", "A2", "weather")
        
        db.clear_all()
        
        sessions = db.get_all_sessions()
        
        assert len(sessions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])