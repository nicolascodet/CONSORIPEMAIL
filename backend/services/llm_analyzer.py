from typing import Dict, List, Optional
import openai
from pydantic import BaseModel
from config import settings

class EmailAnalysis(BaseModel):
    summary: str
    sentiment: str
    key_entities: List[Dict[str, str]]
    action_items: List[str]
    urgency_level: str
    topics: List[str]

class LLMAnalyzer:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.model = "gpt-4"

    async def analyze_email(self, subject: str, body: str, sender: str, recipients: List[str]) -> EmailAnalysis:
        """
        Analyze an email using GPT-4 to extract insights.
        """
        prompt = f"""Analyze this email and provide structured insights:
        From: {sender}
        To: {', '.join(recipients)}
        Subject: {subject}
        Body: {body}

        Provide a detailed analysis including:
        1. A concise summary
        2. Overall sentiment (positive, negative, or neutral)
        3. Key entities (people, organizations) mentioned
        4. Action items or requests
        5. Urgency level
        6. Main topics discussed
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert email analyzer. Extract key information and insights from emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            # Parse the response
            analysis = response.choices[0].message.content
            
            # Extract structured information from the analysis
            # This is a simplified version - in production, you'd want more robust parsing
            analysis_lines = analysis.split('\n')
            summary = ""
            sentiment = "neutral"
            key_entities = []
            action_items = []
            urgency_level = "normal"
            topics = []

            current_section = ""
            for line in analysis_lines:
                line = line.strip()
                if "Summary:" in line:
                    current_section = "summary"
                    summary = line.split("Summary:")[1].strip()
                elif "Sentiment:" in line:
                    current_section = "sentiment"
                    sentiment = line.split("Sentiment:")[1].strip().lower()
                elif "Entities:" in line or "Key entities:" in line:
                    current_section = "entities"
                elif "Action items:" in line:
                    current_section = "actions"
                elif "Urgency:" in line:
                    urgency_level = line.split("Urgency:")[1].strip().lower()
                elif "Topics:" in line:
                    current_section = "topics"
                elif line and current_section:
                    if current_section == "entities" and ":" in line:
                        entity_type, entity_name = line.split(":", 1)
                        key_entities.append({
                            "type": entity_type.strip(),
                            "name": entity_name.strip()
                        })
                    elif current_section == "actions" and line.startswith("-"):
                        action_items.append(line[1:].strip())
                    elif current_section == "topics" and line.startswith("-"):
                        topics.append(line[1:].strip())

            return EmailAnalysis(
                summary=summary,
                sentiment=sentiment,
                key_entities=key_entities,
                action_items=action_items,
                urgency_level=urgency_level,
                topics=topics
            )

        except Exception as e:
            print(f"Error analyzing email: {e}")
            raise

    async def analyze_thread(self, emails: List[Dict]) -> Dict:
        """
        Analyze an email thread to provide a comprehensive summary and insights.
        """
        thread_prompt = "Analyze this email thread and provide insights:\n\n"
        for email in emails:
            thread_prompt += f"""
            From: {email['sender']}
            Time: {email['timestamp']}
            Subject: {email['subject']}
            Body: {email['body']}
            ---
            """

        thread_prompt += """
        Provide:
        1. Thread summary
        2. Key discussion points
        3. Overall sentiment
        4. Action items
        5. Participants and their roles
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing email threads and extracting key insights."},
                    {"role": "user", "content": thread_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            return {
                "analysis": response.choices[0].message.content,
                "thread_length": len(emails)
            }

        except Exception as e:
            print(f"Error analyzing thread: {e}")
            raise

    async def analyze_attachment_content(self, content: str, filename: str) -> Dict:
        """
        Analyze the content of an email attachment.
        """
        prompt = f"""Analyze this document content from file '{filename}':

        {content[:4000]}  # Limit content length for token constraints

        Provide:
        1. Document summary
        2. Key points
        3. Document type and purpose
        4. Action items or next steps
        5. Important dates or deadlines mentioned
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing document content and extracting key information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            return {
                "analysis": response.choices[0].message.content,
                "filename": filename
            }

        except Exception as e:
            print(f"Error analyzing attachment: {e}")
            raise
