import logging

logger = logging.getLogger()

# HTTP STATUS CODE

# Command Pattern
# CREATE - POST
# READ - GET
# UPDATE - PUT
# DELETE _ DELETE

# Dispatch Table

ROUTES = {
    # ("GET", "/plants/{id}"): get_plant_by_id,
    # ("POST", "/plants/{id}"): create_plant_by_id,
    # ("PUT", "/plants/{id}"): update_plant_by_id,
    # ("DELETE", "/plants/{id}"): delete_plant_by_id,
}


# Decorator - Register handlers into Dispatch Table (Route)
def route(method: str, path: str):
    def decorator (func):
        logger.info(f"Registering {method} {path}")
        ROUTES [(method, path)] = func
        logger.info(f"Registered {len(ROUTES)} routes")
        return func
    return decorator
