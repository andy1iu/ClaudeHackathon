#!/usr/bin/env python3
"""
Reset briefings and chat conversations while keeping patient data intact.
Run this script to clear all briefings and conversations from the database.
"""
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.patient import ClinicalBriefing, ChatConversation


def reset_briefings():
    """Delete all briefings and conversations from the database"""
    
    print("🔄 Resetting briefings and conversations...")
    print("   (Patient data, EHR records, and narratives will remain intact)")
    print()
    
    db = Session(engine)
    
    try:
        # Count before deletion
        briefing_count = db.query(ClinicalBriefing).count()
        conversation_count = db.query(ChatConversation).count()
        
        print(f"📊 Found:")
        print(f"   • {briefing_count} briefings")
        print(f"   • {conversation_count} conversations")
        print()
        
        # Delete all briefings
        db.query(ClinicalBriefing).delete()
        
        # Delete all conversations
        db.query(ChatConversation).delete()
        
        db.commit()
        
        print("✅ Successfully deleted:")
        print(f"   • {briefing_count} briefings")
        print(f"   • {conversation_count} conversations")
        print()
        print("🎉 Reset complete!")
        print("   All patients can now start fresh intake processes.")
        
    except Exception as e:
        print(f"❌ Error during reset: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_briefings()

