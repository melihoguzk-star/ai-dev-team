# GET /api/posts Endpoint — FastAPI Implementation

## 1. FastAPI Endpoint Kodu

```python
"""
Posts API - FastAPI ile basit bir blog post servisi.
In-memory data store kullanır, pagination destekler.
"""

from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class PostResponse(BaseModel):
    """Tek bir blog post'unun response modeli."""
    id: int
    title: str
    content: str
    author: str
    created_at: datetime


class PaginatedPostsResponse(BaseModel):
    """Sayfalanmış post listesi response modeli."""
    items: list[PostResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ---------------------------------------------------------------------------
# In-Memory Data Store
# ---------------------------------------------------------------------------

POSTS_DB: list[dict] = [
    {
        "id": 1,
        "title": "FastAPI Introduction",
        "content": "FastAPI is a modern Python web framework.",
        "author": "melih",
        "created_at": datetime(2026, 3, 1, 10, 0, 0),
    },
    {
        "id": 2,
        "title": "Pydantic V2 Deep Dive",
        "content": "Pydantic V2 brings significant performance improvements.",
        "author": "melih",
        "created_at": datetime(2026, 3, 2, 14, 30, 0),
    },
    {
        "id": 3,
        "title": "Async Python Patterns",
        "content": "Understanding asyncio is key for high-performance APIs.",
        "author": "ahmet",
        "created_at": datetime(2026, 3, 3, 9, 15, 0),
    },
]

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Posts API",
    version="1.0.0",
    description="Basit blog post CRUD servisi",
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/api/v1/posts",
    response_model=PaginatedPostsResponse,
    summary="Tüm postları listele",
    status_code=200,
)
async def list_posts(
    page: int = Query(default=1, ge=1, description="Sayfa numarası (1-tabanlı)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Sayfa başına kayıt"),
) -> PaginatedPostsResponse:
    """
    Tüm postları sayfalanmış biçimde döndürür.

    - **page**: İstenen sayfa numarası (varsayılan: 1)
    - **page_size**: Sayfa başına kayıt sayısı (varsayılan: 10, maks: 100)
    """
    total = len(POSTS_DB)
    total_pages = max(1, -(-total // page_size))  # ceil division

    start = (page - 1) * page_size
    end = start + page_size
    items = [PostResponse(**post) for post in POSTS_DB[start:end]]

    return PaginatedPostsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get(
    "/api/v1/posts/{post_id}",
    response_model=PostResponse,
    summary="Tekil post getir",
    status_code=200,
    responses={404: {"description": "Post bulunamadı"}},
)
async def get_post(post_id: int) -> PostResponse:
    """
    Verilen `post_id` ile eşleşen postu döndürür.
    Bulunamazsa **404 Not Found** döner.
    """
    for post in POSTS_DB:
        if post["id"] == post_id:
            return PostResponse(**post)

    raise HTTPException(status_code=404, detail=f"Post with id={post_id} not found")
```

## 2. Endpoint Dokümantasyonu

### `GET /api/v1/posts` — Tüm Postları Listele

| Özellik        | Değer                          |
| -------------- | ------------------------------ |
| **Method**     | `GET`                          |
| **Path**       | `/api/v1/posts`                |
| **Status**     | `200 OK`                       |

**Query Parameters:**

| Param       | Tip   | Zorunlu | Varsayılan | Açıklama                       |
| ----------- | ----- | ------- | ---------- | ------------------------------ |
| `page`      | `int` | Hayır   | `1`        | Sayfa numarası (min: 1)        |
| `page_size` | `int` | Hayır   | `10`       | Sayfa başına kayıt (1–100)     |

**Response Body (200):**

```json
{
  "items": [
    {
      "id": 1,
      "title": "FastAPI Introduction",
      "content": "FastAPI is a modern Python web framework.",
      "author": "melih",
      "created_at": "2026-03-01T10:00:00"
    }
  ],
  "total": 3,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

### `GET /api/v1/posts/{post_id}` — Tekil Post Getir

| Özellik        | Değer                              |
| -------------- | ---------------------------------- |
| **Method**     | `GET`                              |
| **Path**       | `/api/v1/posts/{post_id}`          |
| **Status**     | `200 OK` / `404 Not Found`        |

**Path Parameters:**

| Param     | Tip   | Açıklama      |
| --------- | ----- | ------------- |
| `post_id` | `int` | Post ID değeri |

**Response Body (200):**

```json
{
  "id": 1,
  "title": "FastAPI Introduction",
  "content": "FastAPI is a modern Python web framework.",
  "author": "melih",
  "created_at": "2026-03-01T10:00:00"
}
```

**Response Body (404):**

```json
{
  "detail": "Post with id=999 not found"
}
```

## 3. Örnek curl Komutları

```bash
# Tüm postları getir (varsayılan pagination)
curl -s http://localhost:8000/api/v1/posts | python -m json.tool

# Sayfa 1, sayfa başına 2 kayıt
curl -s "http://localhost:8000/api/v1/posts?page=1&page_size=2" | python -m json.tool

# Tekil post getir (id=1)
curl -s http://localhost:8000/api/v1/posts/1 | python -m json.tool

# Var olmayan post (404 dönecek)
curl -s -w "\nHTTP Status: %{http_code}\n" http://localhost:8000/api/v1/posts/999
```

**Sunucuyu başlatmak için:**

```bash
uvicorn main:app --reload --port 8000
```
