# Test Transcripts for Travel Assistant

This document contains 4 comprehensive test transcripts designed to test different features and conversation flows of the travel assistant application.

---

## Transcript 1: Destination Recommendation Flow
**Purpose:** Tests destination recommendation with progressive information gathering, value-first approach, and external data fetching.

**User Messages:**
```
1. "I'm looking for a beach destination in December with a budget of $2000"

2. "I'll be traveling from New York"

3. "I prefer warm weather and good food. I'm traveling solo."

4. "Tell me more about the first option"
```

**Expected Behaviors:**
- Message 1: Should ask for origin (budget mentioned but no origin)
- Message 2: Should provide 3 destination recommendations immediately (has budget + origin + timeframe + preferences)
- Message 3: Should acknowledge and possibly refine recommendations or provide additional info
- Message 4: Should provide detailed information about the first recommended destination
- Should fetch country information via research agent for recommendations

---

## Transcript 2: Packing Suggestions with Weather
**Purpose:** Tests packing intent, location/date extraction, weather API integration, and context-aware responses.

**User Messages:**
```
1. "What should I pack for a trip to Tokyo in March?"

2. "I'll be there for 10 days. What about formal wear?"

3. "What's the weather going to be like?"
```

**Expected Behaviors:**
- Message 1: Should extract location (Tokyo) and date (March), fetch weather data, provide packing suggestions based on weather
- Message 2: Should refine packing list considering duration and formal wear needs
- Message 3: Should provide weather forecast information (legitimate intent, conversational follow-up)
- Should call `fetch_weather_for_location` tool via research agent
- Should consider weather data when generating packing suggestions

---

## Transcript 3: Attractions and Local Activities
**Purpose:** Tests attractions intent, location extraction, country info fetching, and multi-turn conversation about activities.

**User Messages:**
```
1. "What are some must-see attractions in Paris?"

2. "Are there any free activities?"

3. "What about day trips from Paris?"
```

**Expected Behaviors:**
- Message 1: Should extract location (Paris), fetch country info, provide list of attractions with practical details (costs, timing, booking needs)
- Message 2: Should filter or highlight free activities from the previous recommendations
- Message 3: Should provide day trip suggestions (legitimate intent, conversational follow-up)
- Should call `fetch_country_info` tool via research agent
- Should provide practical information (costs, timing, booking requirements)

---

## Transcript 4: Visa Information Query
**Purpose:** Tests visa query detection, country extraction (origin + destination), direct tool calling optimization, and visa API integration.

**User Messages:**
```
1. "Do I need a visa to travel to Japan if I'm from the United States?"

2. "What about entry requirements for Brazil?"

3. "I'm actually from Canada, not the US. Check again for Japan."
```

**Expected Behaviors:**
- Message 1: Should detect visa query, extract origin (United States) and destination (Japan), call visa API directly (optimization path), provide visa requirements
- Message 2: Should extract destination (Brazil), ask for or infer origin, provide visa requirements
- Message 3: Should correct origin (Canada), re-query visa API, provide updated information
- Should use direct visa query handling (bypasses LLM function calling for speed)
- Should call `fetch_visa_info` tool with origin and destination countries

---

## Additional Edge Case Tests (Optional)

### Edge Case 1: Fictional Location
**User Message:** "What should I pack for a trip to Hogwarts?"

**Expected Behavior:** Should detect fictional location, respond with witty/humorous message asking for real location (user violation processor)

### Edge Case 2: Unsupported Intent
**User Message:** "Book me a flight to London"

**Expected Behavior:** Should classify as "unsupport" intent, return message: "I'm sorry, but NIR (Navan Intelligent Recommender) does not support your request at this moment..."

### Edge Case 3: Non-Legitimate Intent
**User Message:** "Tell me a joke"

**Expected Behavior:** Should classify as "non_legit" intent, return message: "I'm sorry, I can't help with that. Please ask a question about travel planning."

### Edge Case 4: Vague Destination Query
**User Message:** "Where should I go?"

**Expected Behavior:** Should ask 1-2 clarifying questions about budget, timeframe, or preferences (not overwhelm with many questions)

### Edge Case 5: Complete Information (Immediate Recommendation)
**User Message:** "I want a family-friendly beach destination in July for $4000, traveling from London with kids aged 5 and 8, prefer all-inclusive resorts"

**Expected Behavior:** Should immediately provide 3 destination recommendations without asking follow-up questions (value-first approach with sufficient information)

---

## Testing Checklist

For each transcript, verify:
- [ ] Intent is correctly classified
- [ ] Location is correctly extracted (when applicable)
- [ ] Date is correctly extracted (when applicable)
- [ ] Appropriate external data is fetched (weather/country/visa)
- [ ] Response is contextually appropriate
- [ ] Conversation flow is natural
- [ ] System messages are properly injected
- [ ] Context window management works (for longer conversations)
- [ ] Error handling works gracefully

---

## Notes

- All transcripts assume the conversation starts fresh (conversation reset)
- Weather data is fetched for packing suggestions
- Country info is fetched for destination and attractions queries
- Visa info uses direct tool calling for optimization
- The system prioritizes providing value over asking questions when sufficient information is available

