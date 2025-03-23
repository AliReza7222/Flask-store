"""
Writing swagger structure for user part
https://swagger.io/docs/specification/v2_0/what-is-swagger/
"""

ADD_PRODUCT = {
    "summary": "Add a new product",
    "description": "Adds a new product to the inventory (Admin only).",
    "security": [{"BearerAuth": []}],
    "tags": ["Product"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "description": "Product object that needs to be added",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number", "minimum": 0.01},
                    "inventory": {"type": "integer", "minimum": 0},
                    "description": {"type": "string"},
                },
                "required": ["name", "price", "inventory"],
            },
        },
    ],
    "responses": {
        "201": {
            "description": "Product created successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                    "inventory": {"type": "integer"},
                    "description": {"type": "string"},
                    "created_by": {"type": "integer"},
                    "updated_by": {"type": "integer"},
                    "created_at": {"type": "string"},
                    "updated_at": {"type": "string"},
                },
            },
        },
        "400": {"description": "Bad Request"},
        "401": {"description": "Unauthorized"},
    },
}

DELETE_PRODUCT = {
    "summary": "Delete a product",
    "description": "Deletes a specific product by ID (Admin only).",
    "security": [{"BearerAuth": []}],
    "tags": ["Product"],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "required": True,
            "type": "integer",
        },
    ],
    "responses": {
        "200": {
            "description": "Product successfully deleted",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
            },
        },
        "404": {"description": "Product not found"},
        "401": {"description": "Unauthorized"},
    },
}

GET_PRODUCT = {
    "summary": "Get a product",
    "description": "Retrieves details of a specific product by ID.",
    "tags": ["Product"],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "required": True,
            "type": "integer",
        },
    ],
    "responses": {
        "200": {
            "description": "Product details",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                    "inventory": {"type": "integer"},
                    "description": {"type": "string"},
                    "created_by": {"type": "integer"},
                    "updated_by": {"type": "integer"},
                    "created_at": {"type": "string"},
                    "updated_at": {"type": "string"},
                },
            },
        },
        "404": {"description": "Product not found"},
    },
}

LIST_PRODUCTS = {
    "summary": "List products",
    "description": "Retrieves a paginated list of products.",
    "tags": ["Product"],
    "parameters": [
        {
            "name": "page",
            "in": "query",
            "description": "Page number",
            "required": False,
            "type": "integer",
            "default": 1,
        },
    ],
    "responses": {
        "200": {
            "description": "List of products",
            "schema": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer"},
                    "per_page": {"type": "integer"},
                    "total_products": {"type": "integer"},
                    "total_pages": {"type": "integer"},
                    "has_next": {"type": "boolean"},
                    "has_prev": {"type": "boolean"},
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "price": {"type": "number"},
                                "inventory": {"type": "integer"},
                                "description": {"type": "string"},
                                "created_by": {"type": "integer"},
                                "updated_by": {"type": "integer"},
                                "created_at": {"type": "string"},
                                "updated_at": {"type": "string"},
                            },
                        },
                    },
                },
            },
        },
    },
}

UPDATE_PRODUCT = {
    "summary": "Update a product",
    "description": "Updates details of a specific product (Admin only).",
    "security": [{"BearerAuth": []}],
    "tags": ["Product"],
    "parameters": [
        {
            "name": "product_id",
            "in": "path",
            "description": "ID of the product to update",
            "required": True,
            "type": "integer",
        },
        {
            "name": "body",
            "in": "body",
            "description": "Product object that needs to be updated",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number", "minimum": 0.01},
                    "inventory": {"type": "integer", "minimum": 0},
                    "description": {"type": "string"},
                },
                "required": ["name", "price", "inventory", "description"],
            },
        },
    ],
    "responses": {
        "200": {
            "description": "Product updated successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"},
                    "inventory": {"type": "integer"},
                    "description": {"type": "string"},
                },
            },
        },
        "400": {"description": "Bad Request"},
        "401": {"description": "Unauthorized"},
        "404": {"description": "Product not found"},
    },
}
