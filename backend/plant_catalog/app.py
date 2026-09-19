import json
import logging

from routes import ROUTES
import handlers  # noqa: F401  -- import triggers @route registration; do not remove
from responses import json_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# ========================
# Entry Point
# ========================

def lambda_handler(event, context):
    route_key = (
        event["requestContext"]["http"]["method"],
        event["routeKey"].split(" ", 1)[1]
    )

    handler = ROUTES.get(route_key)

    if handler is None:
        return {
            'statusCode': 404,
            'body': json.dumps('Route not found')
        }

    try:
        return handler(event)
    except Exception as e:
        logger.error(e)
        return json_response(500, {"message": "Internal server error"})
