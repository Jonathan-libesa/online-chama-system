from django import template


register = template.Library()


@register.filter(name='can_apply_loan')
def can_apply_loan(member_loans):
    return not member_loans or any(loan.loan_status in [2, 0, 1] for loan in member_loans)

 