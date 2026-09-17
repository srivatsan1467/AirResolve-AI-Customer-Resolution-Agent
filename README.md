# AirResolve: Customer-Facing Airline Disruption Resolution Agent

A recruiter-friendly Python + Streamlit prototype for AIONOS Assignment 3.

## What it does

AirResolve handles the three supplied customer disruption scenarios:

- Priya Nair — cancelled flight
- Arvind Kulkarni — 4-hour delay
- Meher Kaur — 6-hour delay and ₹2,000 higher-fare request

The agent:
- retrieves customer and booking information
- detects common request intents
- applies the supplied service rules
- identifies allowed actions
- explains policy limits
- escalates requests outside agent authority

## Technology

- Python
- Streamlit
- JSON
- Deterministic policy/decision engine

No external customer data is used.

## Run locally

### Windows

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Demo cases

### Priya

> My flight was cancelled. I want a full cash refund and a free business class upgrade on my return flight.

Expected:
- Full refund can be initiated
- Free business-class upgrade is not covered and requires human review

### Arvind

> My flight is delayed by 4 hours. I want a hotel.

Expected:
- Meal voucher + lounge access
- Hotel is not eligible at 4 hours

### Meher

> I want a full night's hotel stay and a different flight with a ₹2,000 fare difference. Can you waive it?

Expected:
- Hotel is limited to delayed-hours coverage
- ₹2,000 fare-difference waiver requires escalation because it exceeds ₹1,500

## Important data-grounding rule

The prototype uses only the customer profiles, booking data, service rules, allowed/prohibited actions, and scenarios supplied in the Assignment 3 data pack. It does not invent alternative flight numbers, availability, compensation, or policies.
