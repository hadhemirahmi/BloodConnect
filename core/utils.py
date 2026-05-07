BLOOD_COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}

def get_compatible_groups(donor_group):
    """Returns a list of blood groups the donor can give to."""
    return BLOOD_COMPATIBILITY.get(donor_group, [])

def is_compatible(donor_group, recipient_group):
    """Checks if a donor with donor_group can give to a recipient with recipient_group."""
    return recipient_group in get_compatible_groups(donor_group)
