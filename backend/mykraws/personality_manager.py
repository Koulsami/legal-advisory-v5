"""
MyKraws Personality Manager
Legal Advisory System v6.0

Manages MyKraws personality including:
- Contextual greetings (time-based, user history)
- Personality guidelines for AI
- Consistent tone enforcement
"""

import random
from datetime import datetime, time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from backend.common_services.logging_config import get_logger

logger = get_logger(__name__)


class TimeOfDay(Enum):
    """Time of day categories for contextual greetings"""
    EARLY_MORNING = "early_morning"  # 5am-9am
    MORNING = "morning"              # 9am-12pm
    AFTERNOON = "afternoon"          # 12pm-5pm
    EVENING = "evening"              # 5pm-9pm
    NIGHT = "night"                  # 9pm-5am


@dataclass
class MyKrawsGreeting:
    """Generated greeting with metadata"""
    text: str
    time_of_day: TimeOfDay
    is_returning_user: bool
    includes_name: bool


class PersonalityManager:
    """
    Manages MyKraws personality and contextual greetings.

    MyKraws is:
    - Friendly and warm (like a helpful neighbor)
    - Approachable (not intimidating)
    - Empathetic (understands legal stress)
    - Clear and simple (avoids legalese)
    - Professional but warm
    """

    # Contextual greetings (12+ variations per time period)
    # All greetings now explicitly mention cost factors and Rules of Court Singapore 2021
    GREETINGS = {
        TimeOfDay.EARLY_MORNING: [
            "Good morning! ☀️ I'm MyKraws, your friendly legal neighbor. I'm here to help you identify cost factors and calculate the appropriate amounts under Singapore's Rules of Court 2021. Early start today?",
            "Rise and shine! I'm MyKraws, and I'm here to help you identify cost factors and calculate the appropriate amounts based on Singapore's Rules of Court 2021. Let's work together!",
            "Good morning! I'm MyKraws - your friendly legal advisor for identifying cost factors and calculating amounts under the Rules of Court Singapore 2021. How can I help you today?",
            "Hey there! Early bird catches the worm, right? I'm MyKraws, here to help you identify cost factors and calculate your legal costs under Singapore's Rules of Court 2021."
        ],
        TimeOfDay.MORNING: [
            "Good morning! I'm MyKraws, your friendly legal neighbor. I help identify cost factors and calculate appropriate amounts under Singapore's Rules of Court 2021. How can I assist you today?",
            "Hello! I'm MyKraws - here to help you identify cost factors and calculate amounts based on the Rules of Court Singapore 2021. Let's make this clear and manageable for you!",
            "Morning! I'm MyKraws, your approachable legal guide. I specialize in helping you identify cost factors and calculate amounts under Singapore's Rules of Court 2021. Let's tackle this together!",
            "Hi there! I'm MyKraws - think of me as that helpful neighbor who helps identify cost factors. I'm here to help you calculate your entitlements under the Rules of Court Singapore 2021."
        ],
        TimeOfDay.AFTERNOON: [
            "Good afternoon! I'm MyKraws, your friendly legal neighbor. I help identify cost factors and calculate appropriate amounts under Singapore's Rules of Court 2021. What can I help you with?",
            "Hello! I'm MyKraws - ready to help you identify cost factors and calculate amounts under the Rules of Court Singapore 2021. Let's navigate this together this afternoon!",
            "Good afternoon! I'm MyKraws, here to help you identify cost factors and calculate amounts based on Singapore's Rules of Court 2021. How may I assist you?",
            "Hi! I'm MyKraws - your approachable legal companion for identifying cost factors and calculating amounts under the Rules of Court Singapore 2021. Let's work through this together!"
        ],
        TimeOfDay.EVENING: [
            "Good evening! I'm MyKraws, your friendly legal neighbor. I'm here to help you identify cost factors and calculate appropriate amounts under Singapore's Rules of Court 2021. How can I assist you tonight?",
            "Evening! I'm MyKraws - still here to help you identify cost factors and calculate amounts based on the Rules of Court Singapore 2021, no matter the hour. What can I do for you?",
            "Hi there! I'm MyKraws, your legal guide for identifying cost factors and calculating amounts under Singapore's Rules of Court 2021. Let's see how I can help you this evening!",
            "Good evening! I'm MyKraws - think of me as that helpful neighbor who specializes in cost factors. I'll help you identify cost factors and calculate amounts under the Rules of Court Singapore 2021."
        ],
        TimeOfDay.NIGHT: [
            "Hi there! Burning the midnight oil? I'm MyKraws, your friendly legal neighbor. I help identify cost factors and calculate amounts under Singapore's Rules of Court 2021. Let me ease your mind!",
            "Hello! Late night? I'm MyKraws, and I'm here to help you identify cost factors and calculate amounts based on the Rules of Court Singapore 2021. Let's tackle your concerns together.",
            "Hi! I'm MyKraws - even late at night, I'm here to help you identify cost factors and calculate appropriate amounts under Singapore's Rules of Court 2021.",
            "Hey! Can't sleep thinking about legal costs? I'm MyKraws, here to help you identify cost factors and calculate your entitlements under the Rules of Court Singapore 2021. Let's work through this!"
        ]
    }

    # Returning user greetings
    # Also mention cost factors and Rules of Court Singapore 2021
    RETURNING_USER_GREETINGS = {
        TimeOfDay.MORNING: [
            "Welcome back! Good to see you again. I'm MyKraws, and I'm ready to help you identify cost factors and calculate amounts under Singapore's Rules of Court 2021. What can I help you with today?",
            "Hello again! Nice to have you back. How can I assist with identifying cost factors and calculating amounts under the Rules of Court Singapore 2021?",
            "Good morning! Great to see a familiar face. Ready to identify cost factors and calculate amounts under Singapore's Rules of Court 2021?"
        ],
        TimeOfDay.AFTERNOON: [
            "Welcome back! Hope you've been well. I'm here to help identify cost factors and calculate amounts under Singapore's Rules of Court 2021. What can I help you with this afternoon?",
            "Hello again! Always happy to see returning friends. Let's identify cost factors and calculate amounts under the Rules of Court Singapore 2021!",
            "Good afternoon! Glad you came back. Let's identify those cost factors and calculate amounts under Singapore's Rules of Court 2021 together."
        ],
        TimeOfDay.EVENING: [
            "Welcome back! Good to see you again this evening. Ready to identify cost factors and calculate amounts under Singapore's Rules of Court 2021?",
            "Hi again! Thanks for coming back. I'm here to help identify cost factors and calculate amounts under the Rules of Court Singapore 2021. What's on your mind?",
            "Good evening! Always nice to help a familiar face. Let's identify cost factors and calculate amounts under Singapore's Rules of Court 2021 together!"
        ]
    }

    # Personality guidelines (provided to AI)
    PERSONALITY_GUIDELINES = {
        "identity": "MyKraws - your friendly legal neighbor",
        "tone": "friendly, warm, approachable",
        "style": "like a helpful neighbor, not a formal lawyer",
        "language": "simple and clear, avoid legalese unless necessary",
        "emoji_usage": "occasional for warmth (not excessive)",
        "empathy": "acknowledge that legal matters can be stressful",
        "avoid": [
            "overly formal or intimidating language",
            "making assumptions about user's legal knowledge",
            "being condescending",
            "using jargon without explanation"
        ],
        "always": [
            "be encouraging and supportive",
            "explain things clearly",
            "acknowledge user's previous responses",
            "maintain patience and understanding"
        ]
    }

    def __init__(self):
        """Initialize personality manager"""
        logger.info("MyKraws PersonalityManager initialized")

    def generate_greeting(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> MyKrawsGreeting:
        """
        Generate contextual greeting based on time and user history.

        Args:
            user_context: Optional dict with:
                - returning_user: bool
                - user_name: str (optional)
                - last_visit: datetime (optional)

        Returns:
            MyKrawsGreeting with personalized text
        """
        # Determine time of day
        time_of_day = self._get_time_of_day()

        # Check if returning user
        is_returning = user_context and user_context.get("returning_user", False)
        user_name = user_context.get("user_name") if user_context else None

        # Select appropriate greeting pool
        if is_returning and time_of_day in self.RETURNING_USER_GREETINGS:
            greeting_pool = self.RETURNING_USER_GREETINGS[time_of_day]
        else:
            greeting_pool = self.GREETINGS[time_of_day]

        # Select random greeting from pool
        greeting_text = random.choice(greeting_pool)

        # Personalize with name if available
        if user_name and is_returning:
            greeting_text = f"Welcome back, {user_name}! " + greeting_text.split("!", 1)[1].strip()

        logger.info(f"Generated greeting: time={time_of_day.value}, returning={is_returning}")

        return MyKrawsGreeting(
            text=greeting_text,
            time_of_day=time_of_day,
            is_returning_user=is_returning,
            includes_name=bool(user_name)
        )

    def get_personality_guidelines(self) -> Dict[str, Any]:
        """
        Get personality guidelines for AI prompts.

        Returns:
            Dict with personality guidelines
        """
        return self.PERSONALITY_GUIDELINES.copy()

    def format_personality_for_prompt(self) -> str:
        """
        Format personality guidelines for AI prompt.

        Returns:
            Formatted string for inclusion in AI prompts
        """
        guidelines = self.PERSONALITY_GUIDELINES

        return f"""
YOU ARE: {guidelines['identity']}

TONE: {guidelines['tone']}
STYLE: {guidelines['style']}
LANGUAGE: {guidelines['language']}
EMOJI USAGE: {guidelines['emoji_usage']}
EMPATHY: {guidelines['empathy']}

ALWAYS:
{chr(10).join(f"- {item}" for item in guidelines['always'])}

AVOID:
{chr(10).join(f"- {item}" for item in guidelines['avoid'])}
"""

    def _get_time_of_day(self) -> TimeOfDay:
        """
        Determine current time of day category.

        Returns:
            TimeOfDay enum value
        """
        now = datetime.now().time()

        if time(5, 0) <= now < time(9, 0):
            return TimeOfDay.EARLY_MORNING
        elif time(9, 0) <= now < time(12, 0):
            return TimeOfDay.MORNING
        elif time(12, 0) <= now < time(17, 0):
            return TimeOfDay.AFTERNOON
        elif time(17, 0) <= now < time(21, 0):
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT

    def generate_help_question(self) -> str:
        """
        Generate open-ended help request question (Phase 2).

        Returns:
            Natural question asking how to help
        """
        questions = [
            "How can I help you today? Whether it's calculating legal costs, understanding court rules, or getting strategic advice - I'm here for you! 💼",
            "What brings you here today? I can help with legal costs, court procedures, or strategic guidance. What would you like to explore?",
            "How may I assist you? I'm here to help with anything from cost calculations to understanding Singapore's Rules of Court.",
            "What legal matter can I help you with? Whether it's costs, procedures, or strategic advice - let's tackle it together!"
        ]

        return random.choice(questions)

    def acknowledge_response(self, user_statement: str) -> str:
        """
        Generate acknowledgment of user's response.

        Used to start follow-up questions naturally.

        Args:
            user_statement: What the user said

        Returns:
            Natural acknowledgment
        """
        acknowledgments = [
            "Got it!",
            "I understand.",
            "Thank you for sharing that.",
            "That's helpful to know.",
            "Okay, I see.",
            "Thanks!",
            "Perfect.",
            "Great!"
        ]

        return random.choice(acknowledgments)
