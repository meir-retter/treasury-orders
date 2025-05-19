def deci_string(n: int) -> str:
    """
    357 -> "3.57"
    4562 -> "45.62"
    89 -> "0.89"
    100 -> "1.00"
    """
    whole_part = n // 100
    hundredths = n % 100
    return f"{whole_part:,}.{hundredths:02d}"