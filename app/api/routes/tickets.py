from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.ticket import Ticket
from app.db.models.user import User
from app.schemas.ticket import TicketCreate, TicketOut
from app.utils.dependencies import get_current_user
from app.utils import constants as msg  # Importing message constants
from uuid import UUID
import logging

# Router setup for ticket-related endpoints
router = APIRouter(prefix="/tickets", tags=["tickets"])

# Logger for tracking errors and events
logger = logging.getLogger(__name__)

@router.post("/")
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new support ticket for the logged-in user.
    """
    try:
        # Create a Ticket object and associate it with the current user
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            user_id=current_user.id
        )

        # Save the new ticket to the database
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Return success response with the created ticket data
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "status_code": 201,
                "message": msg.TICKET_CREATED_SUCCESSFULLY,
                "data": jsonable_encoder(TicketOut.model_validate(ticket, from_attributes=True))
            }
        )

    except Exception as e:
        # Log error and return internal server error response
        logger.error(f"Ticket creation failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "message": msg.INTERNAL_SERVER_ERROR,
                "data": None
            }
        )


@router.get("/")
def get_user_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all support tickets created by the current user.
    """
    try:
        # Retrieve all tickets for the logged-in user
        tickets = db.query(Ticket).filter(Ticket.user_id == current_user.id).all()
        
        # Convert to serializable format
        data = [jsonable_encoder(TicketOut.model_validate(ticket, from_attributes=True)) for ticket in tickets]

        # Return success response with all ticket data
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "status_code": 200,
                "message": msg.TICKETS_RETRIEVED_SUCCESSFULLY,
                "data": data
            }
        )
    except Exception as e:
        # Log error and return internal server error response
        logger.error(f"Fetching tickets failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "message": msg.INTERNAL_SERVER_ERROR,
                "data": None
            }
        )


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific ticket by its ID for the current user.
    """
    try:
        # Fetch ticket by ID and ensure it belongs to the current user
        ticket = db.query(Ticket).filter(
            Ticket.id == ticket_id,
            Ticket.user_id == current_user.id
        ).first()

        # If ticket not found, return 404 response
        if not ticket:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "status_code": 404,
                    "message": msg.TICKET_NOT_FOUND,
                    "data": None
                }
            )

        # Return ticket details
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "status_code": 200,
                "message": msg.TICKET_RETRIEVED_SUCCESSFULLY,
                "data": jsonable_encoder(TicketOut.model_validate(ticket, from_attributes=True))
            }
        )
    except Exception as e:
        # Log and return server error
        logger.error(f"Fetching ticket failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": 500,
                "message": msg.INTERNAL_SERVER_ERROR,
                "data": None
            }
        )
