import re


def contains_any(text, phrases):
    """
    Returns True if any phrase appears in the user's message.
    """
    t = text.lower()
    return any(p in t for p in phrases)


def detect_intents(message):
    """
    Detect the customer's requested actions.
    """
    t = message.lower()
    intents = []

    if contains_any(
        t,
        ["refund", "money back", "cash back", "reimburse"]
    ):
        intents.append("REFUND_REQUEST")

    if contains_any(
        t,
        [
            "rebook",
            "another flight",
            "different flight",
            "move me",
            "change flight",
            "alternative flight",
            "alternate flight"
        ]
    ):
        intents.append("REBOOK_REQUEST")

    if contains_any(
        t,
        ["meal", "food", "voucher"]
    ):
        intents.append("MEAL_VOUCHER")

    if contains_any(
        t,
        ["lounge"]
    ):
        intents.append("LOUNGE_ACCESS")

    if contains_any(
        t,
        ["hotel", "accommodation", "stay", "room", "night"]
    ):
        intents.append("HOTEL_REQUEST")

    if contains_any(
        t,
        ["upgrade", "business class"]
    ):
        intents.append("UPGRADE_REQUEST")

    if contains_any(
        t,
        ["fare difference", "waive", "waiver"]
    ):
        intents.append("FARE_DIFFERENCE")

    if contains_any(
        t,
        [
            "lawyer",
            "legal action",
            "sue",
            "court",
            "formal complaint",
            "complaint to"
        ]
    ):
        intents.append("LEGAL_OR_FORMAL_COMPLAINT")

    return intents


def extract_fare_difference(message):
    """
    Extract a fare difference amount from the customer's message.

    Examples:
        ₹2,000
        Rs 2000
        INR 2000
        2000 fare difference
    """

    patterns = [
        r"(?:₹|rs\.?\s*|inr\s*)?([\d,]+)\s*(?:fare difference|difference)",
        r"(?:₹|rs\.?\s*|inr\s*)?([\d,]+)"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            message.lower()
        )

        if match:
            try:
                return int(
                    match.group(1).replace(",", "")
                )
            except ValueError:
                return None

    return None


def resolve(customer, booking, message):
    """
    Apply the supplied airline policy to the customer's request.

    Returns:
        intents
        actions
        explanations
        escalations
    """

    intents = detect_intents(message)

    actions = []
    escalations = []
    explanations = []

    status = booking.get(
        "status",
        ""
    ).lower()

    # ========================================================
    # LEGAL / FORMAL COMPLAINT
    # ========================================================

    if "LEGAL_OR_FORMAL_COMPLAINT" in intents:

        escalations.append(
            "Legal or formal complaint handling requires "
            "immediate human-agent escalation."
        )


    # ========================================================
    # CANCELLED FLIGHT
    # ========================================================

    if status == "cancelled":

        # ----------------------------------------------------
        # REFUND
        # ----------------------------------------------------

        if "REFUND_REQUEST" in intents:

            actions.append(
                "Refund request can be initiated."
            )

            explanations.append(
                "Because the airline cancelled the flight, "
                "the customer is entitled to a full refund."
            )

            explanations.append(
                "Refunds are processed within 7 business days "
                "to the original payment method only."
            )


        # ----------------------------------------------------
        # REBOOKING
        # ----------------------------------------------------

        if "REBOOK_REQUEST" in intents:

            actions.append(
                "Free rebooking is permitted on the next "
                "available flight within 24 hours."
            )

            if customer["loyalty_tier"] in [
                "Gold",
                "Platinum"
            ]:

                explanations.append(
                    f"{customer['loyalty_tier']} status provides "
                    "priority access to next-available seats."
                )


        # ----------------------------------------------------
        # UPGRADE
        # ----------------------------------------------------

        if "UPGRADE_REQUEST" in intents:

            escalations.append(
                "A free business-class upgrade is not provided "
                "by the stated policy; human-agent review is required."
            )


        # ----------------------------------------------------
        # FARE DIFFERENCE
        # ----------------------------------------------------

        if "FARE_DIFFERENCE" in intents:

            fare_diff = extract_fare_difference(
                message
            )

            if fare_diff is not None:

                if fare_diff > 1500:

                    escalations.append(
                        f"The stated fare difference of "
                        f"₹{fare_diff:,} is above the "
                        f"₹1,500 agent waiver limit and "
                        f"requires supervisor/human approval."
                    )

                else:

                    explanations.append(
                        f"The stated fare difference is "
                        f"₹{fare_diff:,}. Voluntary rebooking "
                        f"on a higher-fare flight requires "
                        f"payment of the fare difference."
                    )

            else:

                explanations.append(
                    "If a customer voluntarily chooses a "
                    "higher-fare flight, the fare difference "
                    "must be paid. The agent cannot waive "
                    "amounts above ₹1,500 without supervisor approval."
                )


        # ----------------------------------------------------
        # NO SPECIFIC REQUEST
        # ----------------------------------------------------

        if not any(
            x in intents
            for x in [
                "REFUND_REQUEST",
                "REBOOK_REQUEST",
                "UPGRADE_REQUEST",
                "FARE_DIFFERENCE"
            ]
        ):

            explanations.append(
                "For an airline-caused cancellation, the available "
                "choices are free rebooking on the next available "
                "flight within 24 hours or a full refund."
            )


    # ========================================================
    # DELAYED FLIGHT
    # ========================================================

    elif status == "delayed":

        delay = booking.get(
            "delay_hours",
            0
        )


        # ----------------------------------------------------
        # DETERMINE STANDARD ELIGIBILITY
        # ----------------------------------------------------

        if delay < 3:

            eligible = [
                "₹500 meal voucher"
            ]

        elif delay > 5:

            eligible = [
                "meal voucher",
                "lounge access",
                "hotel accommodation covering only "
                "the delayed hours"
            ]

        else:

            eligible = [
                "meal voucher",
                "lounge access"
            ]


        # ----------------------------------------------------
        # MEAL VOUCHER
        # ----------------------------------------------------

        if "MEAL_VOUCHER" in intents:

            if delay < 3:

                actions.append(
                    "₹500 meal voucher is eligible under "
                    "the delay policy."
                )

            else:

                actions.append(
                    "Meal voucher is eligible under "
                    "the delay policy."
                )


        # ----------------------------------------------------
        # LOUNGE ACCESS
        # ----------------------------------------------------

        if "LOUNGE_ACCESS" in intents:

            if delay > 3:

                actions.append(
                    "Lounge access is eligible under "
                    "the delay policy."
                )

            else:

                escalations.append(
                    "Lounge access is not provided for "
                    "a delay under 3 hours."
                )


        # ----------------------------------------------------
        # HOTEL
        # ----------------------------------------------------

        if "HOTEL_REQUEST" in intents:

            if delay > 5:

                actions.append(
                    "Hotel accommodation is eligible for "
                    "the delayed-hours portion only, "
                    "not a full night's stay."
                )

            else:

                explanations.append(
                    f"The delay is {delay} hours. "
                    "Hotel accommodation applies only "
                    "when the delay is more than 5 hours."
                )

                if delay >= 3:

                    actions.append(
                        "Meal voucher is eligible under the delay policy."
                    )

                    actions.append(
                        "Lounge access is eligible under the delay policy."
                    )


        # ----------------------------------------------------
        # REBOOKING
        # ----------------------------------------------------

        if "REBOOK_REQUEST" in intents:

            actions.append(
                "Your request for a different flight has "
                "been identified as a rebooking request."
            )

            explanations.append(
                "The supplied assignment data does not "
                "provide alternative flight availability, "
                "so no specific flight can be promised."
            )


        # ----------------------------------------------------
        # FARE DIFFERENCE
        # ----------------------------------------------------

        if "FARE_DIFFERENCE" in intents:

            fare_diff = extract_fare_difference(
                message
            )

            if fare_diff is not None:

                if fare_diff > 1500:

                    escalations.append(
                        f"The stated fare difference of "
                        f"₹{fare_diff:,} is above the "
                        f"₹1,500 agent waiver limit and "
                        f"requires supervisor/human approval."
                    )

                else:

                    explanations.append(
                        f"The stated fare difference is "
                        f"₹{fare_diff:,}. Voluntary higher-fare "
                        f"rebooking requires payment of the "
                        f"fare difference."
                    )

            else:

                explanations.append(
                    "A customer choosing a higher-fare flight "
                    "must pay the applicable fare difference."
                )


        # ----------------------------------------------------
        # UPGRADE
        # ----------------------------------------------------

        if "UPGRADE_REQUEST" in intents:

            escalations.append(
                "A free upgrade beyond the stated standard "
                "policy is not authorized and requires "
                "human-agent review."
            )


        # ----------------------------------------------------
        # NO SPECIFIC REQUEST
        # ----------------------------------------------------

        if not intents:

            actions.append(
                f"Your {delay}-hour delay qualifies for: "
                + ", ".join(eligible)
                + "."
            )


        # ----------------------------------------------------
        # LOYALTY BENEFIT
        # ----------------------------------------------------

        if customer["loyalty_tier"] in [
            "Gold",
            "Platinum"
        ]:

            explanations.append(
                f"{customer['loyalty_tier']} status provides "
                "priority rebooking, but no additional "
                "compensation beyond standard policy."
            )


    # ========================================================
    # UNKNOWN / UNSUPPORTED STATUS
    # ========================================================

    else:

        explanations.append(
            "The supplied data does not provide an applicable "
            "disruption rule for this booking."
        )


    # ========================================================
    # RETURN DECISION
    # ========================================================

    return {
        "intents": intents,
        "actions": actions,
        "explanations": explanations,
        "escalations": escalations
    }