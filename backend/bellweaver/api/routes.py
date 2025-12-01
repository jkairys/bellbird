"""
Domain-specific route handlers for Bellweaver API.

This module contains all the route handlers organized by domain (users, events, etc.).
"""

from flask import Flask, jsonify, Blueprint
from sqlalchemy import select
from sqlalchemy.orm import Session

from bellweaver.db.database import get_db
from bellweaver.db.models import ApiPayload, Batch
from bellweaver.models.compass import CompassUser, CompassEvent
from bellweaver.parsers.compass import CompassParser

# Create blueprint for user-related routes
user_bp = Blueprint("users", __name__, url_prefix="/user")

# Create blueprint for events-related routes
events_bp = Blueprint("events", __name__, url_prefix="/events")


@user_bp.route("", methods=["GET"])
def get_user():
    """
    Get user details from the latest user batch.

    Fetches the most recent batch for the get_user_details method,
    retrieves all API payloads within that batch, and parses them
    using the CompassUser Pydantic model.

    Returns:
        JSON response with parsed user data or error message

    Example response (single user):
        {
            "batch_id": "uuid-string",
            "created_at": "2025-12-01T12:00:00Z",
            "user": {
                "user_id": 123,
                "user_full_name": "John Doe",
                "user_email": "john@example.com",
                ...
            }
        }

    Example response (multiple users - should be rare):
        {
            "batch_id": "uuid-string",
            "created_at": "2025-12-01T12:00:00Z",
            "users": [
                {...},
                {...}
            ]
        }
    """
    db: Session = next(get_db())
    try:
        # Find the latest batch for get_user_details method
        stmt = (
            select(Batch)
            .where(Batch.method_name == "get_user_details")
            .order_by(Batch.created_at.desc())
            .limit(1)
        )
        latest_batch = db.execute(stmt).scalar_one_or_none()

        if not latest_batch:
            return jsonify({"error": "No user batches found"}), 404

        # Get all API payloads for this batch
        stmt = select(ApiPayload).where(ApiPayload.batch_id == latest_batch.id)
        payloads = db.execute(stmt).scalars().all()

        if not payloads:
            return jsonify({"error": "No payloads found in batch"}), 404

        # Parse each payload using CompassUser model
        users = []
        for payload in payloads:
            raw_data = payload.get_payload()
            try:
                user = CompassParser.parse(CompassUser, raw_data)
                users.append(user.model_dump(mode="json"))
            except Exception as e:
                # Log error but continue processing other payloads
                print(f"Failed to parse payload {payload.id}: {e}")
                continue

        if not users:
            return jsonify({"error": "Failed to parse any user data"}), 500

        # Return single user or list depending on count
        response = {
            "batch_id": latest_batch.id,
            "created_at": latest_batch.created_at.isoformat(),
        }

        if len(users) == 1:
            response["user"] = users[0]
        else:
            response["users"] = users

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    finally:
        db.close()


@events_bp.route("", methods=["GET"])
def get_events():
    """
    Get calendar events from the latest events batch.

    Fetches the most recent batch for the get_calendar_events method,
    retrieves all API payloads within that batch, and parses them
    using the CompassEvent Pydantic model.

    Returns:
        JSON response with parsed event data or error message

    Example response:
        {
            "batch_id": "uuid-string",
            "created_at": "2025-12-01T12:00:00Z",
            "parameters": {
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "limit": 100
            },
            "event_count": 42,
            "events": [
                {
                    "activity_id": 123,
                    "title": "School Assembly",
                    "description": "Whole school assembly",
                    "start": "2025-12-05T09:00:00Z",
                    "finish": "2025-12-05T10:00:00Z",
                    ...
                },
                ...
            ]
        }
    """
    db: Session = next(get_db())
    try:
        # Find the latest batch for get_calendar_events method
        stmt = (
            select(Batch)
            .where(Batch.method_name == "get_calendar_events")
            .order_by(Batch.created_at.desc())
            .limit(1)
        )
        latest_batch = db.execute(stmt).scalar_one_or_none()

        if not latest_batch:
            return jsonify({"error": "No calendar event batches found"}), 404

        # Get all API payloads for this batch
        stmt = select(ApiPayload).where(ApiPayload.batch_id == latest_batch.id)
        payloads = db.execute(stmt).scalars().all()

        if not payloads:
            return jsonify({"error": "No payloads found in batch"}), 404

        # Parse each payload using CompassEvent model
        events = []
        parse_errors = []
        for payload in payloads:
            raw_data = payload.get_payload()
            try:
                event = CompassParser.parse(CompassEvent, raw_data)
                events.append(event.model_dump(mode="json"))
            except Exception as e:
                # Log error but continue processing other payloads
                parse_errors.append({"payload_id": payload.id, "error": str(e)})
                continue

        if not events:
            return jsonify({
                "error": "Failed to parse any event data",
                "parse_errors": parse_errors
            }), 500

        # Build response with batch metadata
        response = {
            "batch_id": latest_batch.id,
            "created_at": latest_batch.created_at.isoformat(),
            "parameters": latest_batch.parameters,
            "event_count": len(events),
            "events": events,
        }

        # Include parse errors if any occurred
        if parse_errors:
            response["parse_errors"] = parse_errors

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    finally:
        db.close()


def register_routes(app: Flask) -> None:
    """
    Register all route blueprints with the Flask application.

    Args:
        app: The Flask application instance
    """
    app.register_blueprint(user_bp)
    app.register_blueprint(events_bp)
