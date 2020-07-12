def is_phone_valid(phone: str):
    if not phone[0] == '+':
        return False
    if not len(phone) == 13:
        return False
    if not phone[1:].isdigit():
        return False
    return True


def is_email_valid(email: str):
    s = email.find('@', 1, -4)
    if s == -1:
        return False
    d = email.find('.', s + 2, len(email) - 2)
    if d == -1:
        return False
    if email[s - 1] == '.' or email[0] == '.':
        return False
    for i in range(s):
        if not any([email[i].isdigit(), email[i].isalpha(), email[i] == '.']):
            return False
    for i in range(s + 1, len(email)):
        if not any([email[i].isdigit(), email[i].isalpha(), email[i] == '.']):
            return False
    return True


def is_age_valid(age: str):
    return age.isdigit()
