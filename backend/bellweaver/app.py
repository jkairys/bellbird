"""
Flask application factory for Bellweaver API.

Provides REST API endpoints for accessing aggregated school calendar events.
"""

from flask import Flask, jsonify
from sqlalchemy import select
from sqlalchemy.orm import Session

from bellweaver.db.database import get_db, init_db
from bellweaver.db.models import ApiPayload, Batch
from bellweaver.models.compass import CompassUser
from bellweaver.parsers.compass import CompassParser


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Initialize database on startup
    with app.app_context():
        init_db()

    @app.route("/user", methods=["GET"])
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

    return app


if __name__ == "__main__":
    import os
    app = create_app()
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, host="0.0.0.0", port=5000, use_reloader=debug)
