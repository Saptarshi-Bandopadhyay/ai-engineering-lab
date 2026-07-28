```markdown
# REST API Documentation (Version 1)

## Authentication

### POST /users
Registers a new user.

**Request**
```json
{
    "email": "john@example.com",
    "password": "password123"
}

```

**Responses**

* `201 Created`
```json
{
    "id": 1,
    "email": "john@example.com"
}

```


* `409 Conflict`: Email already registered.
* `422 Unprocessable Entity`: Invalid email format or password requirements not met.

### POST /login

Authenticates a user and returns a token.

**Request**

```json
{
    "email": "john@example.com",
    "password": "password123"
}

```

**Responses**

* `200 OK`
```json
{
    "access_token": "eyJhbGciOiJIUzI1...",
    "token_type": "Bearer"
}

```


* `401 Unauthorized`: Invalid credentials.
* `422 Unprocessable Entity`: Invalid request format.

### GET /me

Returns the currently authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Responses**

* `200 OK`
```json
{
    "id": 1,
    "email": "john@example.com"
}

```


* `401 Unauthorized`: Missing or invalid token.

---

## Conversations

### GET /conversations

Retrieves a list of conversations for the authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Responses**

* `200 OK`
```json
[
    {
        "id": 15,
        "title": "Machine Learning",
        "created_at": "2026-07-28T12:00:00Z"
    }
]

```


* `401 Unauthorized`: Missing or invalid token.

### POST /conversations

Creates a new conversation.

**Headers:** `Authorization: Bearer <token>`

**Request**

```json
{
    "title": "Machine Learning"
}

```

**Responses**

* `201 Created`
```json
{
    "id": 15,
    "title": "Machine Learning",
    "created_at": "2026-07-28T12:00:00Z"
}

```


* `401 Unauthorized`: Missing or invalid token.
* `422 Unprocessable Entity`: Missing required fields.

### GET /conversations/{conversation_id}

Retrieves a specific conversation.

**Headers:** `Authorization: Bearer <token>`

**Responses**

* `200 OK`
```json
{
    "id": 15,
    "title": "Machine Learning",
    "created_at": "2026-07-28T12:00:00Z",
    "updated_at": "2026-07-28T12:05:00Z"
}

```


* `401 Unauthorized`: Missing or invalid token.
* `403 Forbidden`: User does not own this conversation.
* `404 Not Found`: Conversation does not exist.

### PATCH /conversations/{conversation_id}

Updates a specific conversation's attributes (e.g., renaming).

**Headers:** `Authorization: Bearer <token>`

**Request**

```json
{
    "title": "Deep Learning Optimization"
}

```

**Responses**

* `200 OK`
```json
{
    "id": 15,
    "title": "Deep Learning Optimization",
    "created_at": "2026-07-28T12:00:00Z",
    "updated_at": "2026-07-28T12:15:00Z"
}

```


* `401 Unauthorized`: Missing or invalid token.
* `403 Forbidden`: User does not own this conversation.
* `404 Not Found`: Conversation does not exist.
* `422 Unprocessable Entity`: Invalid request body.

### DELETE /conversations/{conversation_id}

Deletes a specific conversation.

**Headers:** `Authorization: Bearer <token>`

**Request**
*(No body required)*

**Responses**

* `204 No Content`
* `401 Unauthorized`: Missing or invalid token.
* `403 Forbidden`: User does not own this conversation.
* `404 Not Found`: Conversation does not exist.

```

```