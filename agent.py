import json
from policy_engine import resolve, detect_intents

class AirResolveAgent:
    def __init__(self, data_path="data.json"):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get_customer(self, name):
        return self.data["customers"].get(name)

    def get_primary_booking(self, name):
        customer = self.get_customer(name)
        if not customer:
            return None
        return customer["bookings"][0]

    def respond(self, customer_name, message):
        customer = self.get_customer(customer_name)
        if not customer:
            return {
                "reply": "I could not find that customer in the supplied assignment data.",
                "actions": [],
                "escalations": []
            }

        booking = self.get_primary_booking(customer_name)
        result = resolve(customer, booking, message)

        parts = []
        parts.append(
            f"I've checked booking {customer['booking_reference']} for {customer_name}. "
            f"Flight {booking['flight']} ({booking['route']}) is currently {booking['status'].lower()}."
        )

        if booking["status"].lower() == "delayed":
            parts.append(
                f"The recorded delay is {booking['delay_hours']} hours, with the new departure at {booking['new_departure']}."
            )
        elif booking["status"].lower() == "cancelled":
            parts.append("The cancellation is recorded as being due to operational reasons.")

        if result["actions"]:
            parts.append("\n".join("✓ " + a for a in result["actions"]))

        if result["explanations"]:
            parts.append("\n".join(result["explanations"]))

        if result["escalations"]:
            parts.append("\n".join("⚠ " + e for e in result["escalations"]))

        if not result["actions"] and not result["escalations"] and not result["explanations"]:
            parts.append("I can help with the disruption options covered by the supplied policy.")

        return {
            "reply": "\n\n".join(parts),
            "actions": result["actions"],
            "escalations": result["escalations"],
            "intents": result["intents"]
        }
