from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Loan, Payment  # Import your Loan and Payment models
from paypalrestsdk import Payment as PayPalPayment
from django.conf import settings

@csrf_exempt
def payment_success(request):
    # Retrieve the payment ID from the query parameters
    payment_id = request.GET.get('paymentId')

    if not payment_id:
        # Handle the case where the payment ID is not available
        messages.error(request, 'Invalid payment ID.')
        return redirect('home')  # Redirect to the home page or another appropriate view

    try:
        # Retrieve the payment details from PayPal
        paypal_payment = PayPalPayment.find(payment_id)
        if paypal_payment.state == 'approved':
            # Payment is approved, update your database or perform other actions
            # For example, you might update the payment status in your database
            loan_id = paypal_payment.transactions[0].custom  # Assuming you've set 'custom' field as loan_id during payment creation
            loan = get_object_or_404(Loan, id=loan_id)

            # Create a Payment instance and save it to the database
            payment_instance = Payment(
                loan=loan,
                amount_paid=paypal_payment.transactions[0].amount.total,
                paypal_payment_id=paypal_payment.id,
            )
            payment_instance.save()

            # Update loan status or any other relevant information
            loan.status = 'Paid'
            loan.save()

            # Display a success message to the user
            messages.success(request, 'Payment successful!')
        else:
            # Handle the case where the payment is not approved
            messages.warning(request, 'Payment not approved.')
    except Exception as e:
        # Handle exceptions or errors from the PayPal SDK
        messages.error(request, f'Error retrieving payment details: {str(e)}')

    return render(request, 'loan/payment_success.html')


def payment_cancel(request):
    # Handle the case where the payment is canceled
    messages.warning(request, 'Payment canceled.')
    return render(request, 'loan/payment_cancel.html')