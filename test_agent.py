from agent import AirResolveAgent

agent = AirResolveAgent()

# Priya: refund allowed, upgrade escalated
r = agent.respond("Priya Nair", "I want a full cash refund and a free business class upgrade on my return flight.")
assert any("Refund request" in x for x in r["actions"])
assert any("business-class" in x for x in r["escalations"])

# Arvind: hotel not eligible at 4 hours
r = agent.respond("Arvind Kulkarni", "My flight is delayed by 4 hours. I want a hotel.")
assert not any("Hotel accommodation is eligible" in x for x in r["actions"])
assert any("only when the delay is more than 5 hours" in x for x in r["explanations"])

# Meher: 6-hour hotel coverage + 2,000 fare waiver escalation
r = agent.respond("Meher Kaur", "I want a full night's hotel stay and a different flight with a ₹2,000 fare difference. Can you waive it?")
assert any("delayed-hours portion only" in x for x in r["actions"])
assert any("₹2,000" in x and "₹1,500" in x for x in r["escalations"])

print("All tests passed.")
