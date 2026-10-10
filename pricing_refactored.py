import datetime

TAX = 0.07
member_points = {}
LOG = []

QUANTITY_DISCOUNTS = ((100, 0.9), (50, 0.95))


def _subtotal_for_items(items):
    subtotal = 0
    for item in items:
        quantity = item[1]
        if quantity <= 0:
            continue

        line_total = quantity * item[2]
        for minimum_quantity, discount_rate in QUANTITY_DISCOUNTS:
            if quantity >= minimum_quantity:
                line_total = line_total * discount_rate
                break
        subtotal = subtotal + line_total
    return subtotal


def _apply_member_discount(subtotal, member):
    if member is not None:
        if member not in member_points:
            member_points[member] = 0
        subtotal = subtotal * 0.95
        member_points[member] = member_points[member] + int(subtotal / 100)
    return subtotal


def _apply_coupon(subtotal, coupon, today):
    if coupon is not None:
        if coupon == "SAVE50":
            subtotal = subtotal - 50
        elif coupon == "HALF":
            subtotal = subtotal * 0.5
        elif coupon == "NEWYEAR":
            if today is None:
                today = datetime.date.today()
            if today.month == 1:
                subtotal = subtotal * 0.8
    return subtotal


def _add_tax_and_round(subtotal):
    if subtotal < 0:
        subtotal = 0
    subtotal = subtotal + subtotal * TAX
    return round(subtotal, 2)


def calc(items, member=None, coupon=None, today=None):
    subtotal = _subtotal_for_items(items)
    subtotal = _apply_member_discount(subtotal, member)
    subtotal = _apply_coupon(subtotal, coupon, today)
    total = _add_tax_and_round(subtotal)
    LOG.append((member, total))
    return total
