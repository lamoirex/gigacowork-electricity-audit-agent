def matches_summary(answer, template):
    """Allow line breaks between counters while checking every field."""
    actual_head, marker, actual_body = answer.strip().partition("Причины:")
    expected_head, _, expected_body = template.strip().partition("Причины:")
    if not marker:
        return False

    actual_fields = [
        field.strip() for line in actual_head.strip().splitlines() for field in line.split("|")
    ]
    expected_fields = [field.strip() for field in expected_head.strip().split("|")]
    return actual_fields == expected_fields and actual_body.split() == expected_body.split()
