import json
import os
import secrets
from datetime import date
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Application

User = get_user_model()

@csrf_exempt
def add_job_api(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    # Validate Auth Token
    auth_header = request.headers.get('Authorization')
    bot_secret = os.environ.get('BOT_SECRET')
    
    if not bot_secret:
        return JsonResponse({"error": "BOT_SECRET not configured on server."}, status=500)

    if not auth_header or not auth_header.startswith('Bearer '):
        return JsonResponse({"error": "Missing or invalid Authorization header."}, status=401)
    
    token = auth_header.split(' ')[1]
    if not secrets.compare_digest(token, bot_secret):
        return JsonResponse({"error": "Unauthorized. Invalid token."}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    # Validate required fields
    username = data.get('username')
    email = data.get('email')  # Optional email check
    company = data.get('company')
    role = data.get('role')

    if not username and not email:
        return JsonResponse({"error": "Missing required field: username or email."}, status=400)
    
    if not company or not role:
        return JsonResponse({"error": "Missing required fields: company, role."}, status=400)

    # Validate email format if provided
    if email:
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"error": "Invalid email format."}, status=400)

    # Get User
    try:
        if username:
            user = User.objects.get(username=username)
        else:
            user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": f"User not found."}, status=404)

    # Get optional fields with defaults
    status = data.get('status', 'Applied')
    valid_statuses = ['Wishlist', 'Applied', 'Interview', 'Rejected', 'Offer']
    if status not in valid_statuses:
        status = 'Applied'

    location = data.get('location', '')
    job_url = data.get('job_url', '')
    notes = data.get('notes', '')

    applied_date_str = data.get('applied_date')
    if applied_date_str:
        try:
            applied_date = date.fromisoformat(applied_date_str)
        except ValueError:
            return JsonResponse({"error": "Invalid applied_date format. Use YYYY-MM-DD."}, status=400)
    else:
        applied_date = date.today()
        
    app = Application.objects.create(
        user=user,
        company=company,
        role=role,
        location=location,
        status=status,
        applied_date=applied_date,
        job_url=job_url,
        notes=notes
    )

    return JsonResponse({
        "success": True,
        "id": app.id,
        "message": f"Logged: {role} at {company}"
    }, status=201)
