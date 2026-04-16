"""
Psychological indicators and survey definitions.
Based on validated screening concepts (PHQ-9, GAD-7, and general distress).
Each item uses 0–3 scale: Not at all, Several days, More than half the days, Nearly every day.
Survey questions can be managed in Django admin (Question model); if any exist, they are used.
"""
from dataclasses import dataclass
from typing import List


@dataclass
class SurveyItem:
    category: str
    text: str
    reverse: bool = False  # If True, higher raw score = better (e.g. support)


# Default survey items (used when no Question records in admin)
DEFAULT_SURVEY_ITEMS: List[SurveyItem] = [
    # Mood / depression
    SurveyItem('mood', 'Little interest or pleasure in doing things'),
    SurveyItem('mood', 'Feeling down, depressed, or hopeless'),
    SurveyItem('mood', 'Feeling bad about yourself or that you are a failure'),
    SurveyItem('mood', 'Feeling that you have let yourself or your family down'),
    SurveyItem('mood', 'Feeling distant or cut off from other people'),
    SurveyItem('mood', 'Experiencing unexpected feelings of sadness or crying spells'),
    SurveyItem('mood', 'Having trouble feeling positive emotions'),
    # Anxiety
    SurveyItem('anxiety', 'Feeling nervous, anxious, or on edge'),
    SurveyItem('anxiety', 'Not being able to stop or control worrying'),
    SurveyItem('anxiety', 'Worrying too much about different things'),
    SurveyItem('anxiety', 'Trouble relaxing or feeling restless'),
    SurveyItem('anxiety', 'Being so restless that it is hard to sit still'),
    SurveyItem('anxiety', 'Becoming easily annoyed or irritable'),
    SurveyItem('anxiety', 'Feeling afraid as if something awful might happen'),
    # Sleep
    SurveyItem('sleep', 'Trouble falling or staying asleep'),
    SurveyItem('sleep', 'Sleeping too much'),
    SurveyItem('sleep', 'Waking up feeling unrefreshed'),
    SurveyItem('sleep', 'Having disturbing dreams or nightmares'),
    SurveyItem('sleep', 'Trouble getting out of bed in the morning'),
    # Energy
    SurveyItem('energy', 'Feeling tired or having little energy'),
    SurveyItem('energy', 'Feeling physically exhausted without a clear reason'),
    SurveyItem('energy', 'Poor appetite'),
    SurveyItem('energy', 'Overeating or eating too much'),
    SurveyItem('energy', 'Moving or speaking so slowly that other people could have noticed'),
    # Concentration
    SurveyItem('concentration', 'Trouble concentrating on things, such as reading or work'),
    SurveyItem('concentration', 'Making careless mistakes due to lack of focus'),
    SurveyItem('concentration', 'Finding it difficult to make everyday decisions'),
    SurveyItem('concentration', 'Frequently losing your train of thought'),
    SurveyItem('concentration', 'Memory lapses or forgetting important details'),
    # Hopelessness
    SurveyItem('hopelessness', 'Thoughts that you would be better off dead'),
    SurveyItem('hopelessness', 'Thoughts of hurting yourself in some way'),
    SurveyItem('hopelessness', 'Feeling that your future looks dark or bleak'),
    SurveyItem('hopelessness', 'Believing nothing will ever change for the better'),
    SurveyItem('hopelessness', 'Feeling trapped or finding no way out of your situations'),
    # Support
    SurveyItem('support', 'I feel that there is no one I can share my worries with'),
    SurveyItem('support', 'I have people I can turn to when I need emotional support', reverse=True),
    SurveyItem('support', 'I feel isolated even when I am surrounded by people'),
    SurveyItem('support', 'I have a supportive community or friends who understand me', reverse=True),
    SurveyItem('support', 'People around me are generally unsupportive'),
    SurveyItem('support', 'I feel my relationships are fulfilling and supportive', reverse=True),
]

# Lazy-loaded from DB or default (set by get_survey_items())
SURVEY_ITEMS: List[SurveyItem] = list(DEFAULT_SURVEY_ITEMS)


def get_survey_items() -> List[SurveyItem]:
    """
    Return survey items from Django admin (Question model) if any exist,
    otherwise return the default hardcoded list.
    """
    try:
        from .models import Question
        qs = Question.objects.all().order_by('order', 'id')
        if qs.exists():
            return [SurveyItem(category=q.category, text=q.text, reverse=q.reverse) for q in qs]
    except Exception:
        pass
    return list(DEFAULT_SURVEY_ITEMS)


def get_category_indices(items: List[SurveyItem]) -> dict:
    """Build category -> list of indices for the given items."""
    indices = {}
    for i, item in enumerate(items):
        indices.setdefault(item.category, []).append(i)
    return indices


def score_category(answers: List[int], category: str, items: List[SurveyItem] = None, category_indices: dict = None) -> int:
    """Sum raw answers for a category. Uses items/category_indices if provided, else module defaults."""
    items = items or SURVEY_ITEMS
    indices = category_indices or get_category_indices(items)
    indices = indices.get(category, [])
    total = 0
    for i in indices:
        if i < len(answers) and i < len(items):
            val = answers[i]
            item = items[i]
            if item.reverse:
                val = 4 - val  # reverse so higher = more suffering
            total += val
    return total


def compute_total_and_risk(answers: List[int], items: List[SurveyItem] = None) -> tuple:
    """
    Compute total score and risk level from raw answers (0–3 each).
    Uses get_survey_items() when items is None (admin-managed or default questions).
    Returns (total_score, risk_level, recommendation, category_scores_dict).
    """
    items = items or get_survey_items()
    category_indices = get_category_indices(items)
    if len(answers) < len(items):
        answers = answers + [0] * (len(items) - len(answers))

    mood = score_category(answers, 'mood', items, category_indices)
    anxiety = score_category(answers, 'anxiety', items, category_indices)
    sleep = score_category(answers, 'sleep', items, category_indices)
    energy = score_category(answers, 'energy', items, category_indices)
    concentration = score_category(answers, 'concentration', items, category_indices)
    hopelessness = score_category(answers, 'hopelessness', items, category_indices)
    support = score_category(answers, 'support', items, category_indices)

    total = mood + anxiety + sleep + energy + concentration + hopelessness + support

    # Risk bands (similar in spirit to PHQ-9 total: 0–4 minimal, 5–9 mild, 10–14 moderate, 15–19 moderately severe, 20+ severe)
    # Our scale has more items so we use proportional bands
    max_possible = 4 * len(items)
    if total <= max_possible * 0.12:
        risk_level = 'minimal'
        recommendation = (
            'Your responses suggest minimal signs of distress. Continue to take care of yourself '
            'and reach out to friends or professionals if things change.'
        )
    elif total <= max_possible * 0.26:
        risk_level = 'mild'
        recommendation = (
            'Your responses suggest mild difficulty. Consider self-care, rest, and talking to someone '
            'you trust. If symptoms persist, a check-in with a health professional can help.'
        )
    elif total <= max_possible * 0.40:
        risk_level = 'moderate'
        recommendation = (
            'Your responses suggest moderate distress. It may help to speak with a doctor, counselor, '
            'or mental health professional. You don\'t have to face this alone.'
        )
    elif total <= max_possible * 0.55:
        risk_level = 'moderately_severe'
        recommendation = (
            'Your responses suggest significant distress. We encourage you to reach out to a mental '
            'health professional or your doctor soon. Support is available.'
        )
    else:
        risk_level = 'severe'
        recommendation = (
            'Your responses suggest severe distress. Please consider reaching out to a mental health '
            'professional, a crisis line, or emergency services if you are in crisis. You matter.'
        )

    if hopelessness >= 2:  # Any endorsement of self-harm item
        recommendation = (
            'If you are having thoughts of hurting yourself, please reach out now: '
            'National Suicide Prevention Lifeline (US): 988. '
            'International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/. '
            'Your life matters.'
        )

    return total, risk_level, recommendation, {
        'mood_score': mood,
        'anxiety_score': anxiety,
        'sleep_score': sleep,
        'energy_score': energy,
        'concentration_score': concentration,
        'hopelessness_score': hopelessness,
        'support_score': support,
    }
