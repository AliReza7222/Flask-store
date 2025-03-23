ADD_ORDER = {
    "tags": ["Order"],
    "summary": "Create a new order",
    "description": "Creates a new order for the authenticated user.",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "integer"},
                                "quantity": {"type": "integer"},
                            },
                            "required": ["product_id", "quantity"],
                        },
                    },
                },
                "required": ["items"],
            },
        },
    ],
    "responses": {
        "201": {
            "description": "Order created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "tracking_code": {"type": "string"},
                    "total_price": {"type": "number"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "integer"},
                                "quantity": {"type": "integer"},
                            },
                        },
                    },
                },
            },
        },
        "400": {"description": "Invalid input"},
    },
}

GET_ORDER = {
    "tags": ["Order"],
    "summary": "Get order by tracking code",
    "description": "Retrieves an order using its tracking code.",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "tracking_code",
            "in": "path",
            "type": "string",
            "required": True,
        },
    ],
    "responses": {
        "200": {
            "description": "Order retrieved successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "tracking_code": {"type": "string"},
                    "total_price": {"type": "number"},
                    "items": {
                        "type": "array",
                        "items": {
                            "properties": {
                                "id": {"type": "integer"},
                                "order_id": {"type": "integer"},
                                "product_id": {"type": "integer"},
                                "product_price": {"type": "number"},
                                "quantity": {"type": "integer"},
                            },
                        },
                    },
                },
            },
        },
        "404": {"description": "Order not found"},
    },
}

GET_LIST_ORDERS = {
    "tags": ["Order"],
    "summary": "Get list of orders",
    "description": "Retrieves a paginated list of \
        orders for the authenticated user.",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "required": False,
            "description": "Page number (default: 1)",
            "default": 1,
        },
    ],
    "responses": {
        "200": {
            "description": "List of orders",
            "schema": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer"},
                    "per_page": {"type": "integer"},
                    "total_orders": {"type": "integer"},
                    "total_pages": {"type": "integer"},
                    "has_next": {"type": "boolean"},
                    "has_prev": {"type": "boolean"},
                    "orders": {
                        "type": "array",
                        "items": {
                            "properties": {
                                "id": {"type": "integer"},
                                "created_at": {"type": "string"},
                                "status": {"type": "string"},
                                "total_price": {"type": "number"},
                                "tracking_code": {"type": "string"},
                                "user_id": {"type": "integer"},
                            },
                        },
                    },
                },
            },
        },
    },
}

DELETE_PENDNG_ORDER = {
    "tags": ["Order"],
    "summary": "Delete a pending order",
    "description": "Deletes a pending order if it \
        belongs to the authenticated user.",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "integer",
            "required": True,
        },
    ],
    "responses": {
        "200": {"description": "Order deleted successfully"},
        "404": {"description": "Order not found"},
        "403": {"description": "Order is not in 'Pending' status"},
    },
}

CONFIRMED_ORDER = {
    "tags": ["Order"],
    "summary": "Confirm an order",
    "description": "Marks a pending order as confirmed.",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "integer",
            "required": True,
        },
    ],
    "responses": {
        "200": {"description": "Order confirmed successfully"},
        "404": {"description": "Order not found"},
    },
}

CANCELED_ORDER = {
    "tags": ["Order"],
    "summary": "Cancel a confirmed order",
    "description": "Cancels a confirmed order and updates inventory.",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "integer",
            "required": True,
        },
    ],
    "responses": {
        "200": {"description": "Order canceled successfully"},
        "404": {"description": "Order not found"},
    },
}

COMPLETED_ORDER = {
    "tags": ["Order"],
    "summary": "Complete an order",
    "description": "Marks a confirmed order as completed \
        (admin access required).",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "integer",
            "required": True,
        },
    ],
    "responses": {
        "200": {"description": "Order completed successfully"},
        "404": {"description": "Order not found"},
    },
}

UPDATE_PENDING_ORDER = {
    "tags": ["Order"],
    "summary": "Update a pending order",
    "description": "Updates a pending order if it was created \
        within the last hour.",
    "security": [{"BearerAuth": []}],
    "parameters": [
        {
            "name": "order_id",
            "in": "path",
            "type": "integer",
            "required": True,
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "integer"},
                                "quantity": {"type": "integer"},
                            },
                            "required": ["product_id", "quantity"],
                        },
                    },
                },
                "required": ["items"],
            },
        },
    ],
    "responses": {
        "200": {
            "description": "Order updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "tracking_code": {"type": "string"},
                    "total_price": {"type": "number"},
                    "items": {
                        "type": "array",
                        "items": {
                            "properties": {
                                "id": {"type": "integer"},
                                "order_id": {"type": "integer"},
                                "product_id": {"type": "integer"},
                                "product_price": {"type": "number"},
                                "quantity": {"type": "integer"},
                            },
                        },
                    },
                },
            },
        },
        "400": {"description": "Invalid input"},
        "404": {"description": "Order not found or too old"},
    },
}
