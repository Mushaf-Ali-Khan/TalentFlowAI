from typing import List, Tuple
from datetime import date, datetime

def calculate_total_experience_years(experiences: List[dict]) -> float:
    """
    Calculate total years of experience, deduplicating overlapping date ranges.
    `experiences` is a list of dicts with 'start_date' and 'end_date' (date objects).
    If 'end_date' is None, it implies the current date.
    """
    if not experiences:
        return 0.0

    ranges: List[Tuple[date, date]] = []
    today = datetime.utcnow().date()

    for exp in experiences:
        start = exp.get("start_date")
        end = exp.get("end_date")
        
        if not start:
            continue
        
        if end is None:
            end = today
            
        if start > end:
            continue # Invalid range
            
        ranges.append((start, end))

    if not ranges:
        return 0.0

    # Sort ranges by start date
    ranges.sort(key=lambda x: x[0])

    merged_ranges = [ranges[0]]
    for current_start, current_end in ranges[1:]:
        last_start, last_end = merged_ranges[-1]

        if current_start <= last_end:
            # Overlapping ranges, merge them by extending the end date if needed
            merged_ranges[-1] = (last_start, max(last_end, current_end))
        else:
            # Non-overlapping range
            merged_ranges.append((current_start, current_end))

    total_days = sum((end - start).days for start, end in merged_ranges)
    total_years = total_days / 365.25

    return round(total_years, 1)
