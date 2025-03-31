import math
from email.header import decode_header

def decode_email_subject(subject):
    decoded_parts = decode_header(subject)
    decoded_subject = ""

    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            # Decode using the provided encoding, defaulting to utf-8
            encoding = encoding if encoding and encoding.lower() != "unknown-8bit" else "utf-8"
            decoded_subject += part.decode(encoding, errors="ignore")
        else:
            decoded_subject += part  # If already a string, just append it

    return decoded_subject


def scale_numbers(a, b, c, max_value, ta, tb):
    """
    Scale numbers a, b, c to not exceed max_value while keeping a above ta and b above tb
    Parameters:
    a, b, c - input numbers
    max_value - maximum allowed sum
    ta - minimum threshold for a
    tb - minimum threshold for b
    Returns: tuple of scaled (a, b, c)
    """
    # Initial sum
    total = a + b + c
    
    # If sum is already less than or equal to max, return original numbers
    if total <= max_value:
        return (a, b, c)
    
    # Calculate initial scaling factor
    scale = max_value / total
    
    # Scale all numbers initially
    a_scaled = a * scale
    b_scaled = b * scale
    c_scaled = c * scale
    
    # Check if a or b fall below their respective thresholds
    if a_scaled < ta or b_scaled < tb:
        # If a is below threshold, fix a and scale b and c
        if a_scaled < ta:
            a_new = ta
            remaining = max_value - a_new
            # Recalculate scale for b and c only
            if b + c > 0:  # Avoid division by zero
                scale_bc = remaining / (b + c)
                b_new = b * scale_bc
                c_new = c * scale_bc
                
                # If b still goes below its threshold, fix b too
                if b_new < tb:
                    b_new = tb
                    c_new = max_value - a_new - b_new
                return (a_new, b_new, c_new)
        
        # If b is below threshold, fix b and scale a and c
        if b_scaled < tb:
            b_new = tb
            remaining = max_value - b_new
            # Recalculate scale for a and c only
            if a + c > 0:  # Avoid division by zero
                scale_ac = remaining / (a + c)
                a_new = a * scale_ac
                c_new = c * scale_ac
                
                # If a still goes below its threshold, fix a too
                if a_new < ta:
                    a_new = ta
                    c_new = max_value - a_new - b_new
                return (a_new, b_new, c_new)
    
    # If no threshold violations, return proportionally scaled numbers
    return (math.round(a_scaled), math.round(b_scaled), math.round(c_scaled))
