import anthropic, config, logging
logger = logging.getLogger(__name__)

def draft_message(name: str, other_person: str, topic: str) -> str:
    pitch, cta = config.OUTREACH_SERVICE_PITCH, config.OUTREACH_SOFT_CTA
    prompt = (
        f"You are a world-class executive outreach expert. Draft a hyper-personalized LinkedIn DM to {name}. "
        f"Context: I saw their comment on {other_person}'s post regarding {topic}. "
        f"Pitch: {pitch}. CTA: {cta}. "
        "Constraint: 4-6 sentences. Tone: Warm but authoritative elite peer-to-peer connection. "
        "Return ONLY the message, no explanations."
    )
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        logger.error(f"Claude drafting failed: {e}")
        return f"Hey {name}, I saw your insightful comment on {other_person}'s post about {topic}. {pitch}. {cta}"