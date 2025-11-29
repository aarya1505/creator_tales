import os
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=api_key)

def get_client():
    global _client
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    if _client is None:
        _client = genai.Client(api_key=api_key)
    return _client


def check_api_key():
    return os.environ.get("GEMINI_API_KEY") is not None


def generate_linkedin_post(topic, niche, tone, length, include_carousel=False):
    length_guide = {
        'short': '50-100 words',
        'medium': '150-250 words',
        'long': '300-500 words'
    }
    
    prompt = f"""You are an expert LinkedIn content strategist. Generate a high-performing LinkedIn post.

Topic: {topic}
Niche/Industry: {niche}
Tone: {tone}
Target Length: {length_guide.get(length, '150-250 words')}

Create a LinkedIn post with the following structure:

1. HOOK (First 2-3 lines that grab attention - this appears before "...see more")
2. BODY (Main content with insights, story, or value)
3. CTA (Call-to-action to encourage engagement)

{'Also provide a 5-slide carousel outline based on this topic.' if include_carousel else ''}

Format your response as JSON with the following structure:
{{
    "hook": "The attention-grabbing opening lines",
    "body": "The main content of the post",
    "cta": "The call-to-action",
    "full_post": "The complete post ready to copy",
    "carousel": ["Slide 1 content", "Slide 2 content", ...] (only if carousel requested)
}}

Make the content:
- Authentic and personal
- Value-driven with actionable insights
- Formatted with line breaks for readability
- Include relevant emojis sparingly
- Optimized for LinkedIn's algorithm"""

    try:
        client = get_client()
        if client is None:
            return {
                "error": "API key not configured. Please add your Gemini API key.",
                "hook": "API key required",
                "body": "",
                "cta": "",
                "full_post": "Please configure your Gemini API key to use AI features."
            }
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            result = json.loads(response.text)
            return result
    except Exception as e:
        logging.error(f"Error generating post: {e}")
        return {
            "error": str(e),
            "hook": "Error generating content. Please try again.",
            "body": "",
            "cta": "",
            "full_post": "Error generating content. Please try again."
        }


def rewrite_content(original_content, target_tone):
    prompt = f"""You are a LinkedIn content optimization expert. Rewrite the following content to be more engaging and professional for LinkedIn.

Original Content:
{original_content}

Target Tone: {target_tone}

Rewrite this content with:
1. A strong hook that grabs attention
2. Clear structure with line breaks
3. Professional yet authentic voice
4. Improved clarity and impact
5. LinkedIn-optimized formatting
6. Appropriate use of emojis (sparingly)

Format your response as JSON:
{{
    "rewritten_content": "The fully rewritten content",
    "improvements_made": ["List of improvements made"],
    "engagement_tips": ["Tips for better engagement"]
}}"""

    try:
        client = get_client()
        if client is None:
            return {
                "error": "API key not configured. Please add your Gemini API key.",
                "rewritten_content": "Please configure your Gemini API key to use AI features.",
                "improvements_made": [],
                "engagement_tips": []
            }
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error rewriting content: {e}")
        return {
            "error": str(e),
            "rewritten_content": "Error rewriting content. Please try again.",
            "improvements_made": [],
            "engagement_tips": []
        }


def generate_carousel(topic, niche):
    prompt = f"""You are a LinkedIn carousel content expert. Create a compelling 5-slide carousel outline.

Topic: {topic}
Niche/Industry: {niche}

Create a carousel with this structure:
- Slide 1: Hook (Attention-grabbing title/question)
- Slide 2: Problem (Pain point your audience faces)
- Slide 3: Insight (Key realization or data point)
- Slide 4: Solution (Your answer or framework)
- Slide 5: CTA (Call-to-action)

Format your response as JSON:
{{
    "title": "Carousel title",
    "slides": [
        {{"slide_number": 1, "type": "Hook", "headline": "...", "content": "...", "design_tip": "..."}},
        {{"slide_number": 2, "type": "Problem", "headline": "...", "content": "...", "design_tip": "..."}},
        {{"slide_number": 3, "type": "Insight", "headline": "...", "content": "...", "design_tip": "..."}},
        {{"slide_number": 4, "type": "Solution", "headline": "...", "content": "...", "design_tip": "..."}},
        {{"slide_number": 5, "type": "CTA", "headline": "...", "content": "...", "design_tip": "..."}}
    ],
    "caption": "Suggested LinkedIn caption for the carousel post"
}}

Make each slide:
- Concise and scannable
- Visually describable
- Value-packed"""

    try:
        client = get_client()
        if client is None:
            return {
                "error": "API key not configured. Please add your Gemini API key.",
                "title": "API key required",
                "slides": [],
                "caption": "Please configure your Gemini API key to use AI features."
            }
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error generating carousel: {e}")
        return {
            "error": str(e),
            "title": "Error generating carousel",
            "slides": [],
            "caption": ""
        }


def optimize_profile(about, headline, experience, skills):
    prompt = f"""You are a LinkedIn profile optimization expert. Analyze and improve the following LinkedIn profile sections.

Current About Section:
{about if about else 'Not provided'}

Current Headline:
{headline if headline else 'Not provided'}

Current Experience:
{experience if experience else 'Not provided'}

Current Skills:
{skills if skills else 'Not provided'}

Provide optimized versions with:
1. Keyword optimization for LinkedIn search
2. Clear value proposition
3. Engaging storytelling
4. Professional tone
5. Strong calls-to-action

For experience, use the STAR method (Situation, Task, Action, Result).

Format your response as JSON:
{{
    "optimized_about": "Improved About section (max 2600 characters)",
    "headline_variations": ["5 different headline options"],
    "optimized_experience": "Improved experience using STAR method",
    "skills_suggestions": ["10 relevant skills to add"],
    "profile_tips": ["5 additional profile optimization tips"],
    "keyword_suggestions": ["Relevant keywords to include"]
}}"""

    try:
        client = get_client()
        if client is None:
            return {
                "error": "API key not configured. Please add your Gemini API key.",
                "optimized_about": "Please configure your Gemini API key to use AI features.",
                "headline_variations": [],
                "optimized_experience": "",
                "skills_suggestions": [],
                "profile_tips": [],
                "keyword_suggestions": []
            }
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error optimizing profile: {e}")
        return {
            "error": str(e),
            "optimized_about": "Error optimizing profile. Please try again.",
            "headline_variations": [],
            "optimized_experience": "",
            "skills_suggestions": [],
            "profile_tips": [],
            "keyword_suggestions": []
        }


def generate_networking_message(message_type, tone, context, recipient_info):
    message_templates = {
        'recruiter_outreach': 'Reaching out to a recruiter about job opportunities',
        'referral_request': 'Asking someone for a referral to a company',
        'alumni_networking': 'Connecting with alumni for networking',
        'thank_you': 'Thank you message after an interview',
        'follow_up': 'Following up after initial contact or interview',
        'client_pitch': 'Pitching services to a potential client'
    }
    
    prompt = f"""You are a LinkedIn networking expert. Generate a personalized outreach message.

Message Type: {message_templates.get(message_type, message_type)}
Tone: {tone}
Context/Goal: {context if context else 'General networking'}
Recipient Information: {recipient_info if recipient_info else 'Not specified'}

Create a message that:
1. Has a personalized opening (not generic)
2. Shows genuine interest or value
3. Is concise (under 300 characters for connection requests, under 500 for InMail)
4. Has a clear but soft call-to-action
5. Avoids being salesy or pushy

Format your response as JSON:
{{
    "subject_line": "For InMail (optional)",
    "message": "The full message",
    "connection_note": "Shorter version for connection request (under 300 chars)",
    "follow_up_message": "Suggested follow-up if no response",
    "personalization_tips": ["Tips to further personalize"],
    "what_not_to_do": ["Common mistakes to avoid"]
}}"""

    try:
        client = get_client()
        if client is None:
            return {
                "error": "API key not configured. Please add your Gemini API key.",
                "message": "Please configure your Gemini API key to use AI features.",
                "connection_note": "",
                "follow_up_message": "",
                "personalization_tips": [],
                "what_not_to_do": []
            }
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error generating message: {e}")
        return {
            "error": str(e),
            "message": "Error generating message. Please try again.",
            "connection_note": "",
            "follow_up_message": "",
            "personalization_tips": [],
            "what_not_to_do": []
        }


def generate_content_calendar(niche, duration, goals):
    weeks = 4 if duration == 'monthly' else 1
    
    prompt = f"""You are a LinkedIn content strategist. Create a detailed content calendar.

Niche/Industry: {niche}
Duration: {duration} ({weeks} week(s))
Goals: {goals if goals else 'Increase engagement and build personal brand'}

Create a content calendar with:
1. Specific post topics for each day
2. Content type variety (text, carousel, poll, video idea)
3. Best posting times
4. Hashtag suggestions
5. Engagement strategy

Format your response as JSON:
{{
    "calendar_title": "Title for this content plan",
    "strategy_overview": "Brief strategy explanation",
    "weeks": [
        {{
            "week_number": 1,
            "theme": "Weekly theme",
            "days": [
                {{
                    "day": "Monday",
                    "post_type": "Text/Carousel/Poll/Video",
                    "topic": "Specific topic",
                    "hook_idea": "Opening hook suggestion",
                    "best_time": "Suggested posting time in IST (e.g., 10:30 AM IST)",
                    "hashtags": ["relevant", "hashtags"],
                    "engagement_tip": "How to boost engagement"
                }}
            ]
        }}
    ],
    "content_pillars": ["Main content themes to rotate"],
    "monthly_goals": ["Specific measurable goals"],
    "pro_tips": ["Additional strategy tips"]
}}

Include posts for {weeks * 5} weekdays (Monday-Friday).
Make content ideas specific and actionable."""

    try:
        client = get_client()
        if client is None:
            return {
                "error": "API key not configured. Please add your Gemini API key.",
                "calendar_title": "API key required",
                "weeks": [],
                "content_pillars": [],
                "monthly_goals": [],
                "pro_tips": []
            }
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error generating calendar: {e}")
        return {
            "error": str(e),
            "calendar_title": "Error generating calendar",
            "weeks": [],
            "content_pillars": [],
            "monthly_goals": [],
            "pro_tips": []
        }


def generate_analytics_recommendations(analysis_data):
    prompt = f"""You are a LinkedIn analytics expert. Analyze this LinkedIn performance data and provide strategic recommendations.

Analytics Summary:
- Total Posts: {analysis_data.get('total_posts', 0)}
- Date Range: {analysis_data.get('date_range', 'N/A')}
- Average Impressions: {analysis_data.get('avg_impressions', 0)}
- Average Reactions: {analysis_data.get('avg_reactions', 0)}
- Average Comments: {analysis_data.get('avg_comments', 0)}
- Average Shares: {analysis_data.get('avg_shares', 0)}
- Engagement Rate: {analysis_data.get('engagement_rate', 0)}%
- Best Performing Day: {analysis_data.get('best_day', 'N/A')}
- Best Content Type: {analysis_data.get('best_content_type', 'N/A')}

Top Performing Posts:
{json.dumps(analysis_data.get('top_posts', []), indent=2)}

Provide comprehensive recommendations:

Format your response as JSON:
{{
    "performance_summary": "Overall performance assessment",
    "strengths": ["What's working well"],
    "areas_for_improvement": ["What needs work"],
    "reach_recommendations": ["How to increase reach"],
    "timing_recommendations": ["Best times and days to post"],
    "content_recommendations": ["Content type and topic suggestions"],
    "hook_suggestions": ["5 hook templates based on top performers"],
    "what_to_avoid": ["Things to stop doing"],
    "next_7_post_ideas": [
        {{"day": 1, "topic": "...", "type": "...", "hook": "..."}}
    ],
    "engagement_tactics": ["Ways to boost engagement"],
    "growth_forecast": "Expected improvement if recommendations followed"
}}"""

    try:
        client = get_client()
        if client is None:
            return {
                "error": "API key not configured. Please add your Gemini API key.",
                "performance_summary": "Please configure your Gemini API key to use AI features.",
                "strengths": [],
                "areas_for_improvement": [],
                "reach_recommendations": [],
                "timing_recommendations": [],
                "content_recommendations": [],
                "hook_suggestions": [],
                "what_to_avoid": [],
                "next_7_post_ideas": [],
                "engagement_tactics": [],
                "growth_forecast": ""
            }
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            return json.loads(response.text)
    except Exception as e:
        logging.error(f"Error generating recommendations: {e}")
        return {
            "error": str(e),
            "performance_summary": "Error generating recommendations. Please try again.",
            "strengths": [],
            "areas_for_improvement": [],
            "reach_recommendations": [],
            "timing_recommendations": [],
            "content_recommendations": [],
            "hook_suggestions": [],
            "what_to_avoid": [],
            "next_7_post_ideas": [],
            "engagement_tactics": [],
            "growth_forecast": ""
        }