from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from sse_starlette import EventSourceResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.ticket import Ticket
from app.db.models.message import Message
from app.db.models.user import User
from app.schemas.message import MessageCreate
from app.services.groq import get_groq_response
from app.utils.dependencies import get_current_user
from app.utils import constants as msg
import logging
from uuid import UUID

router = APIRouter(prefix="/tickets", tags=["tickets"])
logger = logging.getLogger(__name__)

@router.post("/{ticket_id}/messages")
def create_message(
    ticket_id: UUID,
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a message to a specific ticket (User & AI response).
    """
    try:
        # import pdb; pdb.set_trace()
        logger.info(f"Received message: {message_in}")
        # Check if ticket exists and belongs to current user
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        ).first()

        if not ticket:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "status_code": 404,
                    "message": "Ticket not found",
                    "data": None
                }
            )

        # Save user's message
        user_msg = Message(
            content=message_in.content,
            ticket_id=ticket.id,
            is_ai=False
        )
        db.add(user_msg)
        db.commit()

        # Get AI response and save it
        ai_response = get_groq_response(message_in.content)

        ai_msg = Message(
            content=ai_response,
            ticket_id=ticket.id,
            is_ai=True
        )
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "status_code": 201,
                "message": "Message created and AI response generated",
                "data": {
                    "user_message": user_msg.content,
                    "ai_message": ai_msg.content
                }
            }
        )

    except Exception as e:
        logger.error(f"Message creation failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "message": msg.INTERNAL_SERVER_ERROR,
                "data": None
            }
        )

@router.get("/{ticket_id}/ai-response")
async def stream_ai_response(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Stream AI response for a specific ticket using Server-Sent Events (SSE).
    """
    try:
        # Check if ticket exists and belongs to current user
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        ).first()

        if not ticket:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "status_code": 404,
                    "message": "Ticket not found",
                    "data": None
                }
            )

        # Fetch the last AI message for this ticket
        ai_message = db.query(Message).filter(
            Message.ticket_id == ticket_id,
            Message.is_ai == True
        ).order_by(Message.created_at.desc()).first()

        if not ai_message:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "status_code": 404,
                    "message": "No AI response found",
                    "data": None
                }
            )

        async def event_stream():
            yield f"data: {ai_message.content}\n\n"

        return EventSourceResponse(event_stream())

    except Exception as e:
        logger.error(f"Streaming AI response failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "message": msg.INTERNAL_SERVER_ERROR,
                "data": None
            }
        )
