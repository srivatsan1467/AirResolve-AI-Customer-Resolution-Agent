import streamlit as st
from agent import AirResolveAgent

st.set_page_config(
    page_title="AirResolve",
    page_icon="✈️",
    layout="wide"
)

# ============================================================
# STYLING
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 0;
}

.subtitle {
    color: #8b95a7;
    font-size: 16px;
    margin-bottom: 24px;
}

/* Customer / booking card */
.status-card {
    border: 1px solid #3b414d;
    border-radius: 12px;
    padding: 18px;
    background: #171a21;
    margin-bottom: 15px;
}

/* Customer chat message */
.chat-user {
    background: #e8f1ff;
    color: #172033;
    padding: 14px 16px;
    border-radius: 12px;
    margin: 10px 0;
    border: 1px solid #c8d9f2;
    line-height: 1.55;
}

.chat-user b {
    color: #173b73;
}

/* Agent chat message */
.chat-agent {
    background: #262a33;
    color: #f5f7fa;
    padding: 14px 16px;
    border-radius: 12px;
    margin: 10px 0;
    white-space: pre-wrap;
    border: 1px solid #3b414d;
    line-height: 1.6;
}

.chat-agent b {
    color: #ffffff;
}

/* Small labels */
.section-label {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: .03em;
    text-transform: uppercase;
    color: #8b95a7;
    margin-bottom: 4px;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
}

/* Improve metric appearance */
[data-testid="stMetric"] {
    background: #1d2129;
    border: 1px solid #343a46;
    padding: 10px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD AGENT
# ============================================================

agent = AirResolveAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "customer" not in st.session_state:
    st.session_state.customer = "Priya Nair"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">✈️ AirResolve</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Customer-Facing Airline Disruption Resolution Agent'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Assignment Demo")

    st.caption(
        "Policy-grounded prototype using the supplied Assignment 3 data."
    )

    customers = list(agent.data["customers"].keys())

    customer = st.selectbox(
        "Select customer",
        customers,
        index=customers.index(st.session_state.customer)
    )

    if customer != st.session_state.customer:
        st.session_state.customer = customer
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("Quick Test Scenarios")

    quick_prompts = {
        "Priya Nair": [
            "My flight was cancelled. I want a full cash refund and a free business class upgrade on my return flight.",
            "I want to rebook my cancelled flight."
        ],

        "Arvind Kulkarni": [
            "My flight is delayed by 4 hours. I want a hotel.",
            "What compensation do I get for this delay?"
        ],

        "Meher Kaur": [
            "I want a full night's hotel stay and a different flight with a ₹2,000 fare difference. Can you waive it?",
            "Can I get lounge access and a hotel for my 6 hour delay?"
        ]
    }

    for i, prompt in enumerate(quick_prompts[customer]):

        if st.button(
            f"Test {i + 1}",
            key=f"quick_{customer}_{i}",
            use_container_width=True
        ):

            result = agent.respond(customer, prompt)

            st.session_state.messages.append(
                ("user", prompt)
            )

            st.session_state.messages.append(
                ("agent", result["reply"])
            )

            st.rerun()

    st.divider()

    if st.button(
        "Clear conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# CUSTOMER INFORMATION
# ============================================================

customer_data = agent.get_customer(
    st.session_state.customer
)

booking = agent.get_primary_booking(
    st.session_state.customer
)


left, right = st.columns([1.45, 1])


# ============================================================
# LEFT: CUSTOMER & BOOKING
# ============================================================

with left:

    st.subheader("Customer & Booking")

    st.markdown(
        '<div class="status-card">',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Customer",
        st.session_state.customer
    )

    c2.metric(
        "Loyalty",
        customer_data["loyalty_tier"]
    )

    c3.metric(
        "Booking",
        customer_data["booking_reference"]
    )

    st.divider()

    d1, d2 = st.columns(2)

    with d1:

        st.write(
            f"**Flight:** {booking['flight']}"
        )

        st.write(
            f"**Route:** {booking['route']}"
        )

        st.write(
            f"**Date:** {booking['date']}"
        )

    with d2:

        st.write(
            f"**Scheduled departure:** "
            f"{booking['scheduled_departure']}"
        )

        if booking["status"].lower() == "delayed":

            st.write(
                f"**New departure:** "
                f"{booking['new_departure']}"
            )

    if booking["status"].lower() == "cancelled":

        st.error("STATUS: CANCELLED")

        st.caption(
            "Reason: Operational reasons"
        )

    else:

        st.warning(
            f"STATUS: DELAYED "
            f"{booking['delay_hours']} HOURS"
        )

        st.caption(
            f"New departure: "
            f"{booking['new_departure']}"
        )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# RIGHT: AGENT AUTHORITY
# ============================================================

with right:

    st.subheader("Agent Authority")

    st.success("Allowed")

    st.write("✓ Rebooking within policy")
    st.write("✓ Meal vouchers")
    st.write("✓ Lounge access")
    st.write("✓ Eligible hotel accommodation")
    st.write("✓ Refund request initiation")

    st.warning("Human escalation")

    st.write("⚠ Exceptions beyond policy")
    st.write("⚠ Fare waiver > ₹1,500")
    st.write("⚠ Legal/formal complaints")
    st.write("⚠ Other prohibited actions")


# ============================================================
# RESOLUTION CHAT
# ============================================================

st.subheader("Resolution Chat")


if not st.session_state.messages:

    st.info(
        "Select a customer and use a Quick Test Scenario, "
        "or type a request below."
    )


for role, content in st.session_state.messages:

    if role == "user":

        st.markdown(
            f'''
            <div class="chat-user">
                <b>You</b><br>
                {content}
            </div>
            ''',
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f'<div class="chat-agent">'
            f'<div class="agent-name">AirResolve</div>'
            f'<div class="agent-message">{content}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Describe your issue or request..."
)

if prompt:

    st.session_state.messages.append(
        ("user", prompt)
    )

    result = agent.respond(
        st.session_state.customer,
        prompt
    )

    st.session_state.messages.append(
        ("agent", result["reply"])
    )

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Prototype note: Responses are grounded only in the "
    "Assignment 3 data pack and do not invent flight availability "
    "or additional compensation."
)