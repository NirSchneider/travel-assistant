DESTINATION_INTENT = "destination"
ATTRACTIONS_INTENT = "attractions"
PACKING_INTENT = "packing"
LEGITIMATE_INTENT = "legitimate"
UNSUPPORTED_INTENT = "unsupport"
NON_LEGIT_INTENT = "non_legit"

VALID_INTENTS = [DESTINATION_INTENT, ATTRACTIONS_INTENT, PACKING_INTENT, LEGITIMATE_INTENT]
NON_VALID_INTENT = [UNSUPPORTED_INTENT, NON_LEGIT_INTENT]

NON_VALID_INTENT_MESSAGES = {
    "unsupport": "I'm sorry, but NIR (Navan Intelligent Recommender) does not support your request at this moment. I can help you with destination recommendations, packing suggestions, and things to do at your destination.",
    "non_legit": "I'm sorry, I can't help with that. Please ask a question about travel planning."
}

