from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_text(text):

    sentiment = analyzer.polarity_scores(text)

    positivity = round(sentiment['pos'] * 100)
    negativity = round(sentiment['neg'] * 100)
    neutrality = round(sentiment['neu'] * 100)

    maturity_score = 50
    empathy = 50
    impulsiveness = 50
    emotional_stability = 50

    text_lower = text.lower()

    if positivity > 40:
        maturity_score += 10
        empathy += 10

    if negativity > 40:
        maturity_score -= 10
        emotional_stability -= 15

    if "hate" in text_lower:
        maturity_score -= 10
        empathy -= 10

    if "understand" in text_lower:
        maturity_score += 10
        empathy += 15

    if "angry" in text_lower:
        impulsiveness += 20

    if len(text.split()) > 40:
        maturity_score += 10

    maturity_age = int(maturity_score / 2 + 15)

    if maturity_score > 65:
        communication_style = "Emotionally mature and balanced"
    elif maturity_score > 50:
        communication_style = "Moderately self-aware"
    else:
        communication_style = "Emotionally reactive"

    return {
        "maturity_age": maturity_age,
        "positivity": positivity,
        "negativity": negativity,
        "neutrality": neutrality,
        "empathy": empathy,
        "impulsiveness": impulsiveness,
        "emotional_stability": emotional_stability,
        "communication_style": communication_style
    }