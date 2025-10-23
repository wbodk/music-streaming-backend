# Music Streaming Backend - API Specification

**Table of Contents**
- [Authentication Endpoints](#authentication-endpoints)
- [Artist Endpoints](#artist-endpoints)
- [Album Endpoints](#album-endpoints)
- [Song Endpoints](#song-endpoints)
- [Error Responses](#error-responses)
- [Authentication](#authentication)

---

## Authentication Endpoints

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required, min 8 chars, digits + symbols)",
  "email": "string (required)",
  "given_name": "string (required)",
  "family_name": "string (required)",
  "birthdate": "string (required, YYYY-MM-DD format)"
}
```

**Response (201):**
```json
{
  "message": "User registration initiated. Check your email for confirmation code.",
  "user_sub": "12345678-1234-1234-1234-123456789012",
  "username": "johndoe"
}
```

**Error Responses:**
- `400` - Missing required fields
- `502` - User already exists or validation error

---

### POST /auth/confirm

Confirm user email with confirmation code received via email.

**Request Body:**
```json
{
  "username": "string (required)",
  "confirmation_code": "string (required, 6-digit code)"
}
```

**Response (200):**
```json
{
  "message": "Email confirmed successfully. You can now login."
}
```

**Error Responses:**
- `400` - Missing required fields
- `502` - Invalid confirmation code, expired code, or user already confirmed

---

### POST /auth/login

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGc...",
  "id_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Error Responses:**
- `400` - Missing username or password
- `401` - Invalid credentials
- `502` - User not confirmed or other auth error

---

### POST /auth/refresh

Refresh expired tokens using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "string (required)"
}
```

**Response (200):**
```json
{
  "message": "Tokens refreshed successfully",
  "access_token": "eyJhbGc...",
  "id_token": "eyJhbGc...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

**Error Responses:**
- `400` - Missing refresh token
- `401` - Invalid or expired refresh token

---

## Artist Endpoints

### GET /artists

Retrieve all artists with pagination.

**Query Parameters:**
```
limit: integer (optional, default 20, max 100)
last_key: string (optional, JSON-encoded pagination token)
```

**Response (200):**
```json
{
  "message": "Artists retrieved successfully",
  "count": 5,
  "artists": [
    {
      "pk": "ARTIST#550e8400-e29b-41d4-a716-446655440000",
      "sk": "METADATA",
      "artist_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Michael Jackson",
      "biography": "King of Pop",
      "profile_image_url": "https://example.com/michael.jpg",
      "genre": "Pop",
      "country": "USA",
      "total_albums": 10,
      "total_songs": 150,
      "created_at": "2025-10-23T10:30:00.123456",
      "updated_at": "2025-10-23T10:30:00.123456"
    }
  ],
  "last_key": null
}
```

**Error Responses:**
- `500` - Internal server error

---

### POST /artists

Create a new artist. **Requires admin authorization.**

**Request Body:**
```json
{
  "name": "string (required)",
  "biography": "string (optional)",
  "profile_image_url": "string (optional)",
  "genre": "string (optional)",
  "country": "string (optional)"
}
```

**Response (201):**
```json
{
  "message": "Artist created successfully",
  "artist": {
    "pk": "ARTIST#550e8400-e29b-41d4-a716-446655440000",
    "sk": "METADATA",
    "artist_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Michael Jackson",
    "biography": "King of Pop",
    "profile_image_url": "https://example.com/michael.jpg",
    "genre": "Pop",
    "country": "USA",
    "total_albums": 0,
    "total_songs": 0,
    "created_at": "2025-10-23T10:30:00.123456",
    "updated_at": "2025-10-23T10:30:00.123456"
  }
}
```

**Error Responses:**
- `400` - Missing required fields
- `403` - Not admin (missing admin group)
- `500` - Internal server error

---

### GET /artists/{artistId}

Retrieve a specific artist by ID.

**Path Parameters:**
```
artistId: string (required, UUID)
```

**Response (200):**
```json
{
  "message": "Artist retrieved successfully",
  "artist": {
    "pk": "ARTIST#550e8400-e29b-41d4-a716-446655440000",
    "sk": "METADATA",
    "artist_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Michael Jackson",
    "biography": "King of Pop",
    "profile_image_url": "https://example.com/michael.jpg",
    "genre": "Pop",
    "country": "USA",
    "total_albums": 10,
    "total_songs": 150,
    "created_at": "2025-10-23T10:30:00.123456",
    "updated_at": "2025-10-23T10:30:00.123456"
  }
}
```

**Error Responses:**
- `400` - Invalid artist ID format
- `404` - Artist not found
- `500` - Internal server error

---

### PUT /artists/{artistId}

Update artist metadata. **Requires admin authorization.**

**Request Body:**
```json
{
  "name": "string (optional)",
  "biography": "string (optional)",
  "profile_image_url": "string (optional)",
  "genre": "string (optional)",
  "country": "string (optional)"
}
```

**Response (200):**
```json
{
  "message": "Artist updated successfully",
  "artist": {
    "pk": "ARTIST#550e8400-e29b-41d4-a716-446655440000",
    "sk": "METADATA",
    "artist_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Michael Jackson",
    "biography": "King of Pop - Updated",
    "profile_image_url": "https://example.com/michael.jpg",
    "genre": "Pop/Rock",
    "country": "USA",
    "total_albums": 10,
    "total_songs": 150,
    "created_at": "2025-10-23T10:30:00.123456",
    "updated_at": "2025-10-23T11:45:00.654321"
  }
}
```

**Error Responses:**
- `400` - No valid fields to update
- `403` - Not admin
- `404` - Artist not found
- `500` - Internal server error

---

### DELETE /artists/{artistId}

Delete an artist. **Requires admin authorization.**

**Path Parameters:**
```
artistId: string (required, UUID)
```

**Response (204):**
```
(no content)
```

**Error Responses:**
- `400` - Invalid artist ID format
- `403` - Not admin
- `404` - Artist not found
- `500` - Internal server error

---

## Album Endpoints

### GET /albums

Retrieve all albums with pagination.

**Query Parameters:**
```
limit: integer (optional, default 20, max 100)
last_key: string (optional, JSON-encoded pagination token)
```

**Response (200):**
```json
{
  "message": "Albums retrieved successfully",
  "count": 5,
  "albums": [
    {
      "pk": "ALBUM#550e8400-e29b-41d4-a716-446655440000",
      "sk": "METADATA",
      "album_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Thriller",
      "artist_id": "660e8400-e29b-41d4-a716-446655440001",
      "artist_name": "Michael Jackson",
      "release_date": "1982-11-30",
      "genre": "Pop",
      "description": "Best-selling album of all time",
      "cover_image_url": "https://example.com/thriller.jpg",
      "total_songs": 3,
      "created_at": "2025-10-23T10:30:00.123456",
      "updated_at": "2025-10-23T10:30:00.123456"
    }
  ],
  "last_key": null
}
```

**Error Responses:**
- `500` - Internal server error

---

### POST /albums

Create a new album. **Requires admin authorization.**

**Request Body:**
```json
{
  "title": "string (required)",
  "artist_id": "string (required, UUID of artist)",
  "release_date": "string (optional, YYYY-MM-DD)",
  "genre": "string (optional)",
  "description": "string (optional)",
  "cover_image_url": "string (optional)"
}
```

**Response (201):**
```json
{
  "message": "Album created successfully",
  "album": {
    "pk": "ALBUM#550e8400-e29b-41d4-a716-446655440000",
    "sk": "METADATA",
    "album_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Thriller",
    "artist": "Michael Jackson",
    "release_date": "1982-11-30",
    "genre": "Pop",
    "description": "Best-selling album of all time",
    "cover_image_url": "https://example.com/thriller.jpg",
    "total_songs": 0,
    "created_at": "2025-10-23T10:30:00.123456",
    "updated_at": "2025-10-23T10:30:00.123456"
  }
}
```

**Error Responses:**
- `400` - Missing required fields
- `403` - Not admin (missing admin group)
- `500` - Internal server error

---

### GET /albums/{albumId}

Retrieve a specific album by ID.

**Path Parameters:**
```
albumId: string (required, UUID)
```

**Response (200):**
```json
{
  "message": "Album retrieved successfully",
  "album": {
    "pk": "ALBUM#550e8400-e29b-41d4-a716-446655440000",
    "sk": "METADATA",
    "album_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Thriller",
    "artist": "Michael Jackson",
    "release_date": "1982-11-30",
    "genre": "Pop",
    "description": "Best-selling album of all time",
    "cover_image_url": "https://example.com/thriller.jpg",
    "total_songs": 3,
    "created_at": "2025-10-23T10:30:00.123456",
    "updated_at": "2025-10-23T10:30:00.123456"
  }
}
```

**Error Responses:**
- `400` - Invalid album ID format
- `404` - Album not found
- `500` - Internal server error

---

### PUT /albums/{albumId}

Update album metadata. **Requires admin authorization.**

**Request Body:**
```json
{
  "title": "string (optional)",
  "artist": "string (optional)",
  "release_date": "string (optional, YYYY-MM-DD)",
  "genre": "string (optional)",
  "description": "string (optional)",
  "cover_image_url": "string (optional)"
}
```

**Response (200):**
```json
{
  "message": "Album updated successfully",
  "album": {
    "pk": "ALBUM#550e8400-e29b-41d4-a716-446655440000",
    "sk": "METADATA",
    "album_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Thriller",
    "artist": "Michael Jackson",
    "release_date": "1982-11-30",
    "genre": "Pop/Rock",
    "description": "Updated description",
    "cover_image_url": "https://example.com/thriller.jpg",
    "total_songs": 3,
    "created_at": "2025-10-23T10:30:00.123456",
    "updated_at": "2025-10-23T11:45:00.654321"
  }
}
```

**Error Responses:**
- `400` - No valid fields to update or invalid data
- `403` - Not admin
- `404` - Album not found
- `500` - Internal server error

---

### DELETE /albums/{albumId}

Delete an album. **Requires admin authorization.**

**Path Parameters:**
```
albumId: string (required, UUID)
```

**Response (204):**
```
(no content)
```

**Error Responses:**
- `400` - Invalid album ID format
- `403` - Not admin
- `404` - Album not found
- `500` - Internal server error

---

### GET /albums/{albumId}/songs

Retrieve all songs in a specific album with pagination.

**Path Parameters:**
```
albumId: string (required, UUID)
```

**Query Parameters:**
```
limit: integer (optional, default 20, max 100)
last_key: string (optional, JSON-encoded pagination token)
```

**Response (200):**
```json
{
  "message": "Songs retrieved successfully",
  "album_id": "550e8400-e29b-41d4-a716-446655440000",
  "count": 3,
  "songs": [
    {
      "pk": "SONG#660e8400-e29b-41d4-a716-446655440001",
      "sk": "METADATA",
      "song_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Billie Jean",
      "artist": "Michael Jackson",
      "duration": 294,
      "album_id": "550e8400-e29b-41d4-a716-446655440000",
      "genre": "Pop",
      "s3_key": "songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
      "audio_url": "s3://music-streaming-bucket-218394692060/songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
      "created_at": "2025-10-23T10:35:00.123456",
      "updated_at": "2025-10-23T10:35:00.123456"
    }
  ],
  "last_key": null
}
```

**Error Responses:**
- `400` - Invalid album ID format
- `500` - Internal server error

---

## Song Endpoints

### GET /songs

Retrieve all songs with pagination.

**Query Parameters:**
```
limit: integer (optional, default 20, max 100)
last_key: string (optional, JSON-encoded pagination token)
```

**Response (200):**
```json
{
  "message": "Songs retrieved successfully",
  "count": 5,
  "songs": [
    {
      "pk": "SONG#660e8400-e29b-41d4-a716-446655440001",
      "sk": "METADATA",
      "song_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Billie Jean",
      "artist_id": "550e8400-e29b-41d4-a716-446655440000",
      "artist_name": "Michael Jackson",
      "duration": 294,
      "album_id": "660e8400-e29b-41d4-a716-446655440000",
      "genre": "Pop",
      "s3_key": "songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
      "audio_url": "s3://music-streaming-bucket-218394692060/songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
      "created_at": "2025-10-23T10:35:00.123456",
      "updated_at": "2025-10-23T10:35:00.123456"
    }
  ],
  "last_key": null
}
```

**Error Responses:**
- `500` - Internal server error

---

### POST /songs

Create a new song with audio file. **Requires admin authorization.**

**Request Body:**
```json
{
  "title": "string (required)",
  "artist_id": "string (required, UUID of artist)",
  "duration": "integer (required, seconds)",
  "album_id": "string (required, UUID)",
  "genre": "string (optional)",
  "audio_file": "string (optional, base64-encoded audio)",
  "file_extension": "string (optional, default 'mp3')"
````

---

### POST /songs

Create a new song with audio file. **Requires admin authorization.**

**Request Body:**
```json
{
  "title": "string (required)",
  "artist": "string (required)",
  "duration": "integer (required, seconds)",
  "album_id": "string (required, UUID)",
  "genre": "string (optional)",
  "audio_file": "string (optional, base64-encoded audio)",
  "file_extension": "string (optional, default 'mp3')"
}
```

**Response (201):**
```json
{
  "message": "Song created successfully",
  "song": {
    "pk": "SONG#660e8400-e29b-41d4-a716-446655440001",
    "sk": "METADATA",
    "song_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Billie Jean",
    "artist": "Michael Jackson",
    "duration": 294,
    "album_id": "550e8400-e29b-41d4-a716-446655440000",
    "genre": "Pop",
    "s3_key": "songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "audio_url": "s3://music-streaming-bucket-218394692060/songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "created_at": "2025-10-23T10:35:00.123456",
    "updated_at": "2025-10-23T10:35:00.123456"
  }
}
```

**Error Responses:**
- `400` - Missing required fields
- `403` - Not admin (missing admin group)
- `404` - Album not found
- `500` - Internal server error

---

### GET /songs/{songId}

Retrieve a specific song by ID.

**Path Parameters:**
```
songId: string (required, UUID)
```

**Response (200):**
```json
{
  "message": "Song retrieved successfully",
  "song": {
    "pk": "SONG#660e8400-e29b-41d4-a716-446655440001",
    "sk": "METADATA",
    "song_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Billie Jean",
    "artist_id": "550e8400-e29b-41d4-a716-446655440000",
    "artist_name": "Michael Jackson",
    "duration": 294,
    "album_id": "660e8400-e29b-41d4-a716-446655440000",
    "genre": "Pop",
    "s3_key": "songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "audio_url": "s3://music-streaming-bucket-218394692060/songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "created_at": "2025-10-23T10:35:00.123456",
    "updated_at": "2025-10-23T10:35:00.123456"
  }
}
```

**Error Responses:**
- `400` - Invalid song ID format
- `404` - Song not found
- `500` - Internal server error

---

### PUT /songs/{songId}

Update song metadata. **Requires admin authorization.**

**Request Body:**
```json
{
  "title": "string (optional)",
  "duration": "integer (optional, seconds)",
  "genre": "string (optional)"
}
```

**Response (200):**
```json
{
  "message": "Song updated successfully",
  "song": {
    "pk": "SONG#660e8400-e29b-41d4-a716-446655440001",
    "sk": "METADATA",
    "song_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Billie Jean",
    "artist_id": "550e8400-e29b-41d4-a716-446655440000",
    "artist_name": "Michael Jackson",
    "duration": 300,
    "album_id": "660e8400-e29b-41d4-a716-446655440000",
    "genre": "Pop/Rock",
    "s3_key": "songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "audio_url": "s3://music-streaming-bucket-218394692060/songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "created_at": "2025-10-23T10:35:00.123456",
    "updated_at": "2025-10-23T11:50:00.654321"
  }
}
```

**Error Responses:**
- `400` - No valid fields to update or invalid data
- `403` - Not admin
- `404` - Song not found
- `500` - Internal server error

---

````

**Error Responses:**
- `400` - Invalid song ID format
- `404` - Song not found
- `500` - Internal server error

---

### PUT /songs/{songId}

Update song metadata. **Requires admin authorization.**

**Request Body:**
```json
{
  "title": "string (optional)",
  "artist": "string (optional)",
  "duration": "integer (optional, seconds)",
  "genre": "string (optional)"
}
```

**Response (200):**
```json
{
  "message": "Song updated successfully",
  "song": {
    "pk": "SONG#660e8400-e29b-41d4-a716-446655440001",
    "sk": "METADATA",
    "song_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Billie Jean",
    "artist": "Michael Jackson",
    "duration": 300,
    "album_id": "550e8400-e29b-41d4-a716-446655440000",
    "genre": "Pop/Rock",
    "s3_key": "songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "audio_url": "s3://music-streaming-bucket-218394692060/songs/660e8400-e29b-41d4-a716-446655440001/audio.mp3",
    "created_at": "2025-10-23T10:35:00.123456",
    "updated_at": "2025-10-23T11:50:00.654321"
  }
}
```

**Error Responses:**
- `400` - No valid fields to update or invalid data
- `403` - Not admin
- `404` - Song not found
- `500` - Internal server error

---

### DELETE /songs/{songId}

Delete a song and its audio file from S3. **Requires admin authorization.**

**Path Parameters:**
```
songId: string (required, UUID)
```

**Response (204):**
```
(no content)
```

**Error Responses:**
- `400` - Invalid song ID format
- `403` - Not admin
- `404` - Song not found
- `500` - Internal server error

---

## Authentication

### Token Structure

All protected endpoints require the `Authorization` header with a Bearer token (id_token from login response):

### Admin Authorization

The following endpoints require the user to be in the `admin` group:
- `POST /songs` - Create song
- `PUT /songs/{songId}` - Update song
- `DELETE /songs/{songId}` - Delete song
- `POST /albums` - Create album
- `PUT /albums/{albumId}` - Update album
- `DELETE /albums/{albumId}` - Delete album

To add a user to admin group:
```bash
aws cognito-idp admin-add-user-to-group \
  --user-pool-id eu-west-3_wPbw0CPRD \
  --username <username> \
  --group-name admin
```

---

## Error Responses

### Common Error Format

```json
{
  "message": "Error message",
  "error": "Additional error details (optional)"
}
```

## Notes

- **Audio File Size Limit:** 10 MB (API Gateway limit)
- **Recommended Format:** MP3 (size efficient)
- **Token Expiry:** ID tokens expire after 1 hour; use refresh_token for renewal
- **Album-Song Relationship:** When a song is created, it must reference an existing album via `album_id`. When a song is added to an album, the album's `total_songs` counter is automatically incremented
- **CORS:** All endpoints have CORS enabled for all origins (`*`)
- **Pagination:** Use `last_key` from response for next page of results
