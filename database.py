import sqlite3
from datetime import datetime
from typing import List, Dict


class ChatDatabase:
    def __init__(self, db_name: str = "chat_history.db"):
        """Initialize database connection"""
        self.db_name = db_name
        self.create_table()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_table(self):
        """Create chat history table if it doesn't exist"""
        conn = self.get_connection()
        
        # Check if pdf_name column exists, if not add it
        cursor = conn.execute("PRAGMA table_info(chat_history)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'chat_history' not in [table[0] for table in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            # Create new table with pdf_name column
            conn.execute('''
                CREATE TABLE chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    intent TEXT,
                    pdf_name TEXT,
                    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))
                )
            ''')
        elif 'pdf_name' not in columns:
            # Add pdf_name column to existing table
            conn.execute('ALTER TABLE chat_history ADD COLUMN pdf_name TEXT')
        
        conn.commit()
        conn.close()
    
    def insert_message(self, session_id: str, user_query: str, ai_response: str, intent: str = "", pdf_name: str = None):
        """
        Insert a chat message into database
        
        Args:
            session_id: Unique session identifier
            user_query: User's question
            ai_response: AI's answer
            intent: Classified intent (weather/document)
            pdf_name: Name of PDF used (if any)
        """
        conn = self.get_connection()
        conn.execute(
            '''INSERT INTO chat_history 
            (session_id, user_query, ai_response, intent, pdf_name) 
            VALUES (?, ?, ?, ?, ?)''',
            (session_id, user_query, ai_response, intent, pdf_name)
        )
        conn.commit()
        conn.close()
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """
        Get all messages for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages in format [{"role": "human/ai", "content": "..."}]
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT user_query, ai_response 
            FROM chat_history 
            WHERE session_id = ? 
            ORDER BY created_at''',
            (session_id,)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({"role": "human", "content": row['user_query']})
            messages.append({"role": "ai", "content": row['ai_response']})
        
        conn.close()
        return messages
    
    def get_session_pdf(self, session_id: str) -> str:
        """
        Get the PDF name used in a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            PDF name or None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT pdf_name 
            FROM chat_history 
            WHERE session_id = ? AND pdf_name IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 1''',
            (session_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        return row['pdf_name'] if row else None
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Get list of all unique sessions with PDF info
        
        Returns:
            List of sessions with metadata
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                session_id,
                COUNT(*) as message_count,
                MAX(created_at) as last_message,
                (SELECT pdf_name FROM chat_history ch2 
                 WHERE ch2.session_id = chat_history.session_id 
                 AND ch2.pdf_name IS NOT NULL 
                 ORDER BY ch2.created_at DESC LIMIT 1) as pdf_name
            FROM chat_history
            GROUP BY session_id
            ORDER BY last_message DESC
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "session_id": row['session_id'],
                "message_count": row['message_count'],
                "last_message": row['last_message'],
                "pdf_name": row['pdf_name']
            })
        
        conn.close()
        return sessions
    
    def clear_session(self, session_id: str):
        """
        Delete all messages for a session
        
        Args:
            session_id: Session to clear
        """
        conn = self.get_connection()
        conn.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
    
    def clear_all(self):
        """Delete all chat history"""
        conn = self.get_connection()
        conn.execute('DELETE FROM chat_history')
        conn.commit()
        conn.close()


# Test the database
if __name__ == "__main__":
    db = ChatDatabase()
    
    # Test session
    session_id = "test_session_001"
    
    # Insert some messages
    db.insert_message(session_id, "What's the weather in London?", "It's 15°C and cloudy.", "weather")
    db.insert_message(session_id, "What's in the PDF?", "This document discusses...", "document", "sample.pdf")
    
    # Retrieve history
    history = db.get_session_history(session_id)
    print("Chat History:")
    for msg in history:
        print(f"  {msg['role']}: {msg['content']}")
    
    # Get PDF for session
    pdf = db.get_session_pdf(session_id)
    print(f"\nPDF used: {pdf}")
    
    # Get all sessions
    sessions = db.get_all_sessions()
    print(f"\nTotal sessions: {len(sessions)}")
    for s in sessions:
        print(f"  {s['session_id']}: {s['message_count']} msgs, PDF: {s['pdf_name']}")
    
    # Clean up test
    db.clear_session(session_id)
    print("\nTest session cleared.")