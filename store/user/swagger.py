"""
Writing swagger structure for user part
https://swagger.io/docs/specification/v2_0/what-is-swagger/
"""

REGISTER_USER = {
    "tags": ["User"],
    "summary": "Register a new user",
    "description": "Registers a new user with an email,\
        password, and optional full name.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "minLength": 8},
                    "full_name": {"type": "string"},
                },
                "required": ["email", "password"],
            },
        },
    ],
    "responses": {
        "201": {
            "description": "User successfully created",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "email": {"type": "string"},
                    "full_name": {"type": "string"},
                },
            },
        },
        "400": {"description": "Invalid input or user already exists"},
    },
}

GET_USER = {
    "tags": ["User"],
    "summary": "Get user details",
    "description": "Fetch details of a user by their ID.",
    "parameters": [
        {
            "name": "user_id",
            "in": "path",
            "required": True,
            "type": "integer",
        },
    ],
    "responses": {
        "200": {
            "description": "User details retrieved",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "email": {"type": "string"},
                    "full_name": {"type": "string"},
                    "active": {"type": "boolean"},
                    "is_admin": {"type": "boolean"},
                },
            },
        },
        "404": {"description": "User not found"},
    },
}

LOGIN_USER = {
    "tags": ["User"],
    "summary": "User login",
    "description": "Authenticate user and return access and refresh tokens.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"},
                },
                "required": ["email", "password"],
            },
        },
    ],
    "responses": {
        "200": {
            "description": "Login successful",
            "schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                },
            },
        },
        "400": {"description": "Missing email or password"},
        "404": {"description": "Invalid email or password"},
    },
}

REFRESH_TOKEN = {
    "tags": ["User"],
    "summary": "Refresh access token",
    "description": "Refresh an expired access \
        token using a valid refresh token.",
    "security": [{"BearerAuth": []}],
    "responses": {
        "200": {
            "description": "New access token generated",
            "schema": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                },
            },
        },
        "401": {"description": "Invalid or missing refresh token"},
    },
}
