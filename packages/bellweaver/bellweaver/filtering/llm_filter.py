"""
LLM-based event filtering using Claude API.

Uses Claude to intelligently filter calendar events based on user configuration.
"""

import json
import re
from typing import List, Dict, Any
import anthropic


class LLMFilter:
    """
    Filter calendar events using Claude API.
    """

    def __init__(self, api_key: str):
        """
        Initialize LLMFilter.

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)

    def filter_events(
        self,
        events: List[Dict[str, Any]],
        user_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Filter events based on user configuration using Claude.

        Args:
            events: List of raw calendar events from Compass
            user_config: User configuration (child, school, filter rules)

        Returns:
            Dictionary with filtered events and reasoning
        """

        # Build prompt
        prompt = self._build_prompt(events, user_config)

        # Call Claude
        message = self.client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Look for JSON block in response
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = json.loads(response_text)
        except json.JSONDecodeError:
            # If parsing fails, return raw response
            result = {"raw_response": response_text, "events": []}

        return result

    def _build_prompt(
        self,
        events: List[Dict[str, Any]],
        user_config: Dict[str, Any]
    ) -> str:
        """Build Claude prompt for filtering events."""

        return f"""
You are helping a parent filter school calendar events to find only the relevant ones for their child.

## Child Profile
- Name: {user_config.get('child_name', 'Unknown')}
- School: {user_config.get('school', 'Unknown')}
- Year Level: {user_config.get('year_level', 'Unknown')}
- Class: {user_config.get('class', 'Unknown')}
- Interests: {', '.join(user_config.get('interests', []))}

## Filtering Rules
{user_config.get('filter_rules', 'No specific rules provided. Include events relevant to the child.')}

## Calendar Events
Below are all calendar events for the next 2 weeks. Evaluate each one and determine if it's relevant to the child based on the profile and rules above.

{json.dumps(events, indent=2, default=str)}

## Task
For each event, provide:
1. Whether it's RELEVANT or NOT_RELEVANT to this child
2. Why (reasoning)
3. Any action needed (e.g., "Permission slip required", "Cost: $25")

Return your response as a JSON array with this structure:
```json
[
  {{
    "event_id": "event_id_from_input",
    "title": "event title",
    "date": "event date",
    "is_relevant": true/false,
    "reason": "explanation of relevance",
    "action_needed": "description of any action or null"
  }}
]
```
"""
