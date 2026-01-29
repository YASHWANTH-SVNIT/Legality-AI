from fastapi import APIRouter, HTTPException, Depends, Header, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import logging
import os
import csv
import io
from dotenv import load_dotenv

from src.services.feedback_manager.feedback_manager import FeedbackManager
from src.rag.vector_store import VectorStore
from src.database import execute_query, get_db_connection

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize singletons
feedback_mgr = FeedbackManager()
vector_store = VectorStore()

# Simple Auth
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "admin123") # Default for demo

def verify_admin(x_api_key: Optional[str] = Header(None)):
    """Simple admin key check"""
    # Allow no-auth for demo if needed, but best to enforce
    if x_api_key != ADMIN_API_KEY:
         raise HTTPException(status_code=403, detail="Invalid admin credentials")
    return True

# --- Feedback Management ---

@router.get("/feedback")
def get_all_feedback(
    limit: int = 50, 
    offset: int = 0,
    category: Optional[str] = None,
    type: Optional[str] = None,
    admin: bool = Depends(verify_admin)
):
    """Get feedback entries with basic filtering"""
    try:
        query = "SELECT * FROM feedback WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if type:
            query += " AND feedback_type = ?"
            params.append(type)
            
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        return execute_query(query, tuple(params))
    except Exception as e:
        logger.error(f"Error getting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/feedback/{id}/status")
def update_feedback_status(id: int, status: str, admin: bool = Depends(verify_admin)):
    """Approve or Reject feedback"""
    if status not in ['approved', 'rejected', 'pending']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    try:
        with get_db_connection() as conn:
            conn.execute("UPDATE feedback SET status = ? WHERE id = ?", (status, id))
        return {"status": "updated", "id": id, "new_status": status}
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/{id}/sync")
def sync_feedback_to_chroma(id: int, admin: bool = Depends(verify_admin)):
    """Sync a verified safe/corrected clause to Chroma DB for future RAG"""
    try:
        # 1. Get feedback details
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM feedback WHERE id = ?", (id,)).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Feedback not found")
            
            feedback_data = dict(row)
        
        # 2. Add to verified clauses table (Gold Standard)
        is_safe = feedback_data['feedback_type'] == 'false-positive' or (feedback_data['feedback_type'] == 'approve-fix' and feedback_data['approved'] == 1)
        risk_level = "safe" if is_safe else "risky"
        
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO verified_clauses (clause_text, category, is_safe, source)
                VALUES (?, ?, ?, 'user-feedback')
            """, (feedback_data['clause_text'], feedback_data['category'], is_safe))
            
            # Update status to approved if it wasn't already
            conn.execute("UPDATE feedback SET status = 'approved' WHERE id = ?", (id,))

        # 3. Add to Chroma DB (Gold Standard collection)
        vector_store.add_verified_clause(
            text=feedback_data['clause_text'],
            category=feedback_data['category'],
            risk_level=risk_level
        )
        
        return {"status": "synced", "id": id, "is_safe": is_safe, "risk_level": risk_level}
    except Exception as e:
        logger.error(f"Error syncing to chroma: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/sync-batch")
def sync_feedback_batch(admin_key: str, admin: bool = Depends(verify_admin)):
    """Sync all approved but unsynced feedback to Chroma"""
    if admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid secondary authentication key")
        
    try:
        with get_db_connection() as conn:
            # We'll mark them as 'synced' in a new column or just use verified_clauses as record.
            # To avoid duplicates, we'll check what's already in verified_clauses or add a 'synced' flag.
            # For simplicity in this demo, let's just sync all 'approved' feedback that hasn't been synced.
            
            rows = conn.execute("""
                SELECT * FROM feedback 
                WHERE status = 'approved' 
                AND feedback_type = 'false-positive'
            """).fetchall()
            
            synced_count = 0
            for row in rows:
                feedback_data = dict(row)
                # Check if already synced (naive check)
                exists = conn.execute("SELECT 1 FROM verified_clauses WHERE clause_text = ?", (feedback_data['clause_text'],)).fetchone()
                if not exists:
                    vector_store.add_verified_clause(
                        text=feedback_data['clause_text'],
                        category=feedback_data['category'],
                        risk_level="safe"
                    )
                    conn.execute("""
                        INSERT INTO verified_clauses (clause_text, category, is_safe, source)
                        VALUES (?, ?, ?, 'user-feedback-batch')
                    """, (feedback_data['clause_text'], feedback_data['category'], True))
                    synced_count += 1
            
            return {"status": "success", "count": synced_count}
    except Exception as e:
        logger.error(f"Batch sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/{id}/resolve")
def resolve_feedback(id: int, admin: bool = Depends(verify_admin)):
    """Legacy resolve endpoint - simply marks as approved"""
    return update_feedback_status(id, "approved", admin)

# --- Verified Clauses (Gold Standard) ---

@router.get("/verified-clauses")
def get_verified_clauses(limit: int = 50, admin: bool = Depends(verify_admin)):
    try:
        return execute_query("SELECT * FROM verified_clauses ORDER BY added_date DESC LIMIT ?", (limit,))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verified-clauses")
def add_verified_clause(
    clause: Dict[str, Any],
    admin: bool = Depends(verify_admin)
):
    """
    Add a clause to confirmed safe/risky dataset
    Expected body: { "text": "...", "category": "...", "is_safe": true }
    """
    try:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO verified_clauses (clause_text, category, is_safe, source, confidence_score)
                VALUES (?, ?, ?, 'manual_admin', 1.0)
            """, (clause['text'], clause['category'], clause['is_safe']))
        return {"status": "added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/verified-clauses/{id}")
def delete_verified_clause(id: int, admin: bool = Depends(verify_admin)):
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM verified_clauses WHERE id = ?", (id,))
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/csv")
def export_data(admin: bool = Depends(verify_admin)):
    """Export all feedback data as CSV"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write Header
        writer.writerow([
            'ID', 'Timestamp', 'Category', 'Type', 'Clause Text', 
            'System Score', 'User Comment', 'Approved'
        ])
        
        # Write Data
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM feedback ORDER BY timestamp DESC").fetchall()
            for row in rows:
                writer.writerow([
                    row['id'],
                    row['timestamp'],
                    row['category'],
                    row['feedback_type'],
                    row['clause_text'],
                    row['system_risk_score'],
                    row['user_comment'],
                    row['approved']
                ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=feedback_data.csv"}
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
