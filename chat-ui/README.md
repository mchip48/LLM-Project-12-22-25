# Chat UI

A modern chat interface for the FastAPI chatbot backend with a dark purple and gold theme.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Make sure your FastAPI backend is running on `http://localhost:8000`

## Features

- iMessage-style chat interface
- Dark theme with purple and gold accents
- Auto-scrolling to latest messages
- Unique conversation ID per session
- Loading indicator with animated dots
- Responsive design

## API Integration

The frontend connects to:
- Endpoint: `POST http://localhost:8000/chat`
- Request: `{ "message": "...", "conversation_id": "..." }`
- Response: `{ "message": "...", "conversation_id": "..." }`
