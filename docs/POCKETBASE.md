# PocketBase Integration Guide

Best practices and troubleshooting for PocketBase in this project.

## Version

- **PocketBase**: v0.35.0
- **Image**: `ghcr.io/muchobien/pocketbase:latest`

## Migration Files

### Location

Migration files are stored in `web/pocketbase/pb_migrations/` and mounted to the container via docker-compose.

### Correct Migration Syntax (v0.35+)

```javascript
// pb_migrations/1687801090_create_jobs.js

migrate((app) => {
    // Check if collection exists
    try {
        let existing = app.findCollectionByNameOrId("jobs")
        if (existing) {
            console.log("Jobs collection already exists, skipping")
            return
        }
    } catch (e) {
        // Collection doesn't exist, create it
    }

    let collection = new Collection({
        type: "base",
        name: "jobs",
        listRule: "",
        viewRule: "",
        createRule: "",
        updateRule: "",
        deleteRule: "",
        fields: [
            {
                type: "text",
                name: "url",
                required: true,
                max: 2048,
            },
            {
                type: "number",
                name: "progress",
                required: false,
                min: 0,
                max: 100,
            },
            {
                type: "date",
                name: "expires_at",
                required: true,
            },
        ],
    })

    app.save(collection)
}, (app) => {
    try {
        let collection = app.findCollectionByNameOrId("jobs")
        app.delete(collection)
    } catch {
        // silent errors
    }
})
```

### Common Migration Mistakes

| Mistake | Error | Fix |
|---------|-------|-----|
| Using `Dao(db)` | `ReferenceError: Dao is not defined` | Use `app` object directly |
| Using `schema` key | Collection not created properly | Use `fields` key instead |
| Using `db` parameter | Various errors | Use `app` parameter |

### Migration Commands

```bash
# Apply migrations (automatic on serve)
docker exec <container> /usr/local/bin/pocketbase migrate up

# Revert last migration
docker exec <container> /usr/local/bin/pocketbase migrate down

# Create new migration
docker exec <container> /usr/local/bin/pocketbase migrate create "migration_name"

# Sync migration history
docker exec <container> /usr/local/bin/pocketbase migrate history-sync
```

## Superuser Management

### Create Superuser via CLI

```bash
docker exec <container> /usr/local/bin/pocketbase superuser upsert EMAIL PASSWORD
```

**Note**: The CLI command may not always work reliably. If login fails after creating a superuser, try:

1. Restart the container
2. Create a new superuser with a different email
3. Use the install URL shown in container logs

### Install URL

On first startup, PocketBase provides a one-time install URL in logs:

```
(!) Launch the URL below in the browser if it hasn't been open already to create your first superuser account:
http://0.0.0.0:8090/_/#/pbinstal/eyJhbGci...
```

Use this URL for initial setup.

## API Access Rules

For development, set all rules to empty string `""` to allow public access:

```javascript
let collection = new Collection({
    // ...
    listRule: "",    // Public list access
    viewRule: "",    // Public view access
    createRule: "",  // Public create access
    updateRule: "",  // Public update access
    deleteRule: "",  // Public delete access
})
```

For production, implement proper authorization rules.

## Field Types

### Supported Field Types

| Type | JavaScript Config | Notes |
|------|-------------------|-------|
| text | `{ type: "text", name: "field", max: 100 }` | Use `max` for length limit |
| number | `{ type: "number", name: "field", min: 0, max: 100 }` | Optional min/max |
| date | `{ type: "date", name: "field" }` | ISO 8601 format |
| autodate | `{ type: "autodate", name: "created", onCreate: true, onUpdate: false }` | Auto-managed timestamps |
| bool | `{ type: "bool", name: "field" }` | |
| email | `{ type: "email", name: "field" }` | |
| url | `{ type: "url", name: "field" }` | |
| file | `{ type: "file", name: "field", maxSelect: 1 }` | |

### Important: created/updated Fields

PocketBase does NOT automatically add `created` and `updated` fields to base collections.
You must explicitly define them in your migration:

```javascript
fields: [
    // ... your fields ...
    {
        type: "autodate",
        name: "created",
        onCreate: true,
        onUpdate: false,
    },
    {
        type: "autodate",
        name: "updated",
        onCreate: true,
        onUpdate: true,
    },
]
```

Without these fields, queries like `?sort=created` will fail with 400 error.

### Date Field Format

PocketBase expects ISO 8601 format for dates:

```
2026-01-06T00:00:00Z
2026-01-06 00:00:00.000Z  (also accepted)
```

Empty dates are returned as empty string `""`, not `null`.

## Pydantic Integration

### Handling Empty Date Fields

PocketBase returns empty dates as `""` instead of `null`. Add a validator:

```python
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Any

class JobResponse(BaseModel):
    created: datetime | None = None
    updated: datetime | None = None
    started_at: datetime | None = None

    @field_validator("started_at", "created", "updated", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any) -> Any:
        """Convert empty string to None for optional datetime fields."""
        if v == "" or v is None:
            return None
        return v
```

### Auto-generated Fields

PocketBase automatically manages these fields (do not include in create requests):

- `id` - Auto-generated unique ID
- `created` - Auto-set on creation
- `updated` - Auto-updated on modification

## Docker Configuration

### docker-compose.yml

```yaml
pocketbase:
  image: ghcr.io/muchobien/pocketbase:latest
  container_name: movie-generator-pocketbase
  restart: unless-stopped
  volumes:
    - pb_data:/pb_data
    - ./pocketbase/pb_migrations:/pb_migrations  # Mount migrations
  ports:
    - "8090:8090"
  healthcheck:
    test: ["CMD", "wget", "--spider", "-q", "http://localhost:8090/api/health"]
    interval: 10s
    timeout: 5s
    retries: 3
```

### Volume Management

```bash
# Reset PocketBase data completely
docker compose down
docker volume rm web_pb_data
docker compose up -d
```

## Troubleshooting

### "Failed to create record" 400 Error

1. Check if the table exists (PocketBase creates it with the collection)
2. Verify field types match the schema
3. Check date format (use ISO 8601)
4. Ensure required fields are provided

### Migration Errors on Startup

1. Check migration file syntax
2. Remove problematic migration files
3. Reset the volume and restart

### Login Credentials Not Working

1. Use the install URL from container logs
2. Create a new superuser with different email
3. Check container logs for authentication errors

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/collections/{name}/records` | GET | List records |
| `/api/collections/{name}/records` | POST | Create record |
| `/api/collections/{name}/records/{id}` | GET | Get record |
| `/api/collections/{name}/records/{id}` | PATCH | Update record |
| `/api/collections/{name}/records/{id}` | DELETE | Delete record |
| `/api/health` | GET | Health check |
| `/_/` | GET | Admin dashboard |

## References

- [PocketBase Documentation](https://pocketbase.io/docs/)
- [JavaScript Migrations](https://pocketbase.io/docs/js-migrations/)
- [Collection Operations](https://pocketbase.io/docs/js-collections/)
- [Web API Reference](https://pocketbase.io/docs/api-collections/)
