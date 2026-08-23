VALID_CRITICALITY = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
}


VALID_ENVIRONMENTS = {
    "DEVELOPMENT",
    "TEST",
    "PRODUCTION_SIMULATION"
}


VALID_STATUSES = {
    "ACTIVE",
    "INACTIVE",
    "RETIRED"
}


def validate_criticality(value: str):

    value = value.upper()

    if value not in VALID_CRITICALITY:
        raise ValueError(
            "Invalid criticality. "
            "Use LOW, MEDIUM, HIGH or CRITICAL."
        )

    return value


def validate_environment(value: str):

    value = value.upper()

    if value not in VALID_ENVIRONMENTS:
        raise ValueError(
            "Invalid environment."
        )

    return value


def validate_status(value: str):

    value = value.upper()

    if value not in VALID_STATUSES:
        raise ValueError(
            "Invalid status."
        )

    return value
