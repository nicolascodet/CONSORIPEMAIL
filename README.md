# Email Analyzer

A powerful email analysis tool that processes PST and MBOX files to extract insights using advanced LLM capabilities.

## Features

- **File Processing**
  - Support for PST and MBOX file formats
  - Efficient email extraction and parsing
  - Attachment handling and storage

- **LLM-Powered Analysis**
  - Email summarization
  - Sentiment analysis
  - Entity recognition (people, organizations)
  - Action item extraction
  - Urgency detection
  - Topic identification
  - Thread analysis
  - Attachment content analysis

- **Data Organization**
  - Contact management
  - Organization tracking
  - Email threading
  - Attachment categorization

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/email-analyzer.git
cd email-analyzer
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```
Edit `.env` and set your OpenAI API key and other configuration options.

4. Set up the frontend:
```bash
cd ../frontend
npm install
```

5. Start the services:
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Usage

1. Visit `http://localhost:3000` in your browser
2. Upload your PST or MBOX file
3. Wait for the processing to complete
4. Explore the analyzed emails with AI-powered insights:
   - View email summaries
   - Check sentiment analysis
   - Review identified entities
   - Track action items
   - Analyze email threads
   - Get attachment insights

## API Endpoints

### Email Analysis
- `GET /emails/{email_id}/analysis` - Get AI analysis for a single email
- `GET /threads/{thread_id}/analysis` - Get AI analysis for an email thread
- `GET /attachments/{attachment_id}/analysis` - Get AI analysis for an attachment
- `GET /emails/search` - Perform semantic search across emails

### Data Management
- `POST /upload` - Upload PST or MBOX files
- `GET /emails` - List all emails
- `GET /contacts` - List all contacts
- `GET /organizations` - List all organizations
- `GET /attachments` - List all attachments

## Technology Stack

- **Backend**
  - FastAPI
  - SQLAlchemy
  - OpenAI GPT-4
  - libpff (PST processing)
  - mailbox (MBOX processing)

- **Frontend**
  - Next.js 13
  - React
  - Tailwind CSS
  - Framer Motion

## Security Considerations

- All email data is processed locally
- OpenAI API calls are made securely with your API key
- No data is stored in the cloud
- Attachments are stored securely in your local filesystem

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
