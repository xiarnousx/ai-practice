# Express.js Backend

A basic Express.js backend server with RESTful API endpoints.

## Features

- ✅ Express.js server setup
- ✅ CORS enabled
- ✅ JSON parsing middleware
- ✅ Request logging
- ✅ Error handling middleware
- ✅ RESTful API routes
- ✅ Environment configuration
- ✅ Development tools (nodemon)

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Create your `.env` file (copy from `.env.example` if needed)
4. Start the development server:
   ```bash
   npm run dev
   ```

### Scripts

- `npm start` - Start the production server
- `npm run dev` - Start the development server with nodemon (auto-restart)

## API Endpoints

### Base URL: `http://localhost:3000`

### Health Check
- `GET /health` - Server health status

### Users API
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Example Request
```bash
# Get all users
curl http://localhost:3000/api/users

# Create a new user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

## Project Structure

```
├── server.js              # Main server file
├── package.json           # Dependencies and scripts
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── middleware/           
│   ├── logger.js         # Request logging middleware
│   └── errorHandler.js   # Error handling middleware
└── routes/
    ├── index.js          # Main route handler
    └── users.js          # User routes
```

## Environment Variables

Create a `.env` file with the following variables:

```env
NODE_ENV=development
PORT=3000
```

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "message": "Error message here"
}
```

## Success Response Format

```json
{
  "success": true,
  "data": {},
  "message": "Optional success message"
}
```

## Next Steps

- Add database integration (MongoDB, PostgreSQL, etc.)
- Implement authentication and authorization
- Add input validation and sanitization
- Set up testing framework
- Add API documentation (Swagger/OpenAPI)
- Implement rate limiting
- Add caching layer
- Set up logging service