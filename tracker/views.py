import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from .models import Application, STATUS_CHOICES
from datetime import date
try:
    from groq import Groq
except ImportError:
    Groq = None

# 'tracker' matches the logger name defined in settings.py LOGGING config
# Every log line will show: [timestamp] LEVEL tracker.views → your message
logger = logging.getLogger('tracker')


def status_choices_for(selected='Applied'):
    """Return list of (val, label, is_selected) so templates need no == operator."""
    return [(val, label, val == selected) for val, label in STATUS_CHOICES]


@login_required
def home(request):
    # Only show THIS user's applications
    apps = Application.objects.filter(user=request.user)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        logger.debug("User '%s' searched for: '%s'", request.user.username, q)
        apps = apps.filter(
            Q(company__icontains=q) | Q(role__icontains=q) | Q(location__icontains=q)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        logger.debug("User '%s' filtered by status: '%s'", request.user.username, status_filter)
        apps = apps.filter(status=status_filter)

    # Sorting
    sort = request.GET.get('sort', '-applied_date')
    valid_sorts = ['applied_date', '-applied_date', 'company', '-company']
    if sort in valid_sorts:
        apps = apps.order_by(sort)

    total_count = apps.count()
    logger.info("Home page loaded for user '%s' — %d application(s) found", request.user.username, total_count)

    # Pagination
    paginator = Paginator(apps, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'tracker/home.html', {
        'page_obj': page_obj,
        'query': q,
        'status_filter': status_filter,
        'sort': sort,
        'status_choices': STATUS_CHOICES,
        'total_count': total_count,
    })


@login_required
def add_application(request):
    if request.method == 'POST':
        company  = request.POST.get('company', '').strip()
        role     = request.POST.get('role', '').strip()
        if not company or not role:
            logger.warning("Add application failed — missing fields. User: '%s'", request.user.username)
            messages.error(request, 'Company and Role are required.')
            return render(request, 'tracker/add.html', {
                'status_choices': status_choices_for(request.POST.get('status', 'Applied')),
                'form_data': request.POST,
            })
        app = Application.objects.create(
            user=request.user,           # Ownership — link to logged-in user
            company=company,
            role=role,
            status=request.POST.get('status', 'Applied'),
            location=request.POST.get('location', '').strip(),
            job_url=request.POST.get('job_url', '').strip(),
            notes=request.POST.get('notes', '').strip(),
            applied_date=date.today(),
        )
        logger.info("New application created — ID: %d, Company: '%s', Role: '%s', User: '%s'",
                    app.pk, company, role, request.user.username)
        messages.success(request, f'Application to {company} added successfully!')
        return redirect('/')

    return render(request, 'tracker/add.html', {
        'status_choices': status_choices_for('Applied'),
        'form_data': None,
    })


@login_required
def detail(request, pk):
    # user=request.user prevents users from viewing each other's apps (returns 404)
    app = get_object_or_404(Application, pk=pk, user=request.user)
    return render(request, 'tracker/detail.html', {'app': app})


@login_required
def edit_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        company = request.POST.get('company', '').strip()
        role    = request.POST.get('role', '').strip()
        if not company or not role:
            messages.error(request, 'Company and Role are required.')
            return render(request, 'tracker/edit.html', {
                'app': app, 'status_choices': STATUS_CHOICES,
            })
        app.company  = company
        app.role     = role
        app.status   = request.POST.get('status', app.status)
        app.location = request.POST.get('location', '').strip()
        app.job_url  = request.POST.get('job_url', '').strip()
        app.notes    = request.POST.get('notes', '').strip()
        d = request.POST.get('applied_date', '')
        if d:
            app.applied_date = d
        app.save()
        logger.info("Application updated — ID: %d, Company: '%s', User: '%s'",
                    pk, app.company, request.user.username)
        messages.success(request, 'Application updated successfully!')
        return redirect(f'/app/{pk}/')

    return render(request, 'tracker/edit.html', {
        'app': app,
        'status_choices': status_choices_for(app.status),
    })


@login_required
def delete_application(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method == 'POST':
        name = app.company
        logger.info("Application deleted — ID: %d, Company: '%s', User: '%s'",
                    pk, name, request.user.username)
        app.delete()
        messages.success(request, f'Application for {name} deleted.')
        return redirect('/')
    return render(request, 'tracker/confirm_delete.html', {'app': app})


@login_required
def dashboard(request):
    all_apps = Application.objects.filter(user=request.user)
    total = all_apps.count()

    status_counts = {s[0]: all_apps.filter(status=s[0]).count() for s in STATUS_CHOICES}

    def rate(key):
        return round(status_counts.get(key, 0) / total * 100, 1) if total else 0

    def pct(key):
        return round(status_counts.get(key, 0) / total * 100) if total else 0

    funnel = [
        {'label': 'Wishlist',  'count': status_counts.get('Wishlist', 0),  'pct': pct('Wishlist'),  'color': '#9CA3AF'},
        {'label': 'Applied',   'count': status_counts.get('Applied', 0),   'pct': pct('Applied'),   'color': '#4F46E5'},
        {'label': 'Interview', 'count': status_counts.get('Interview', 0), 'pct': pct('Interview'), 'color': '#2563EB'},
        {'label': 'Rejected',  'count': status_counts.get('Rejected', 0),  'pct': pct('Rejected'),  'color': '#DC2626'},
        {'label': 'Offer',     'count': status_counts.get('Offer', 0),     'pct': pct('Offer'),     'color': '#059669'},
    ]

    return render(request, 'tracker/dashboard.html', {
        'total': total,
        'status_counts': status_counts,
        'interview_rate': rate('Interview'),
        'offer_rate': rate('Offer'),
        'rejection_rate': rate('Rejected'),
        'recent_apps': all_apps.order_by('-applied_date', '-created_at')[:5],
        'status_choices': STATUS_CHOICES,
        'funnel': funnel,
    })


@login_required
def get_ai_insight(request, pk):
    app = get_object_or_404(Application, pk=pk, user=request.user)

    if not Groq:
        messages.error(request, "Groq library not installed.")
        return redirect(f'/app/{pk}/')

    api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not api_key:
        messages.error(request, "Groq API Key not found in settings.py.")
        return redirect(f'/app/{pk}/')

    try:
        client = Groq(api_key=api_key)
        prompt = f"""
Analyze this job application and provide structured interview preparation.

Company: {app.company}
Role: {app.role}
Notes: {app.notes}

Respond using **Markdown formatting only** with these exact sections:

## Interview Prep Questions
1. [Question one]
2. [Question two]
3. [Question three]

## Tactical Advice
- [One specific, actionable tip]

Rules: Use numbered lists for questions. Use bullet points for advice. Use **bold** for emphasis. Add a blank line between each item. No preamble or intro sentence.
"""
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional career coach."},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
        )

        app.ai_suggestion = chat_completion.choices[0].message.content
        app.ai_chat = []
        app.save()
        logger.info("AI Insight generated for app ID: %d, User: '%s'", pk, request.user.username)
        messages.success(request, "AI Insight generated!")
    except Exception as e:
        logger.error("AI Insight error for app ID: %d — %s", pk, str(e))
        messages.error(request, f"AI Error: {str(e)}")

    return redirect(f'/app/{pk}/')


@login_required
def ask_ai(request, pk):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method != "POST":
        if is_ajax:
            return JsonResponse({'error': 'Invalid request method.'}, status=405)
        return redirect(f'/app/{pk}/')

    app = get_object_or_404(Application, pk=pk, user=request.user)
    user_msg = request.POST.get('message', '').strip()

    if not user_msg:
        if is_ajax:
            return JsonResponse({'error': 'Empty message.'}, status=400)
        return redirect(f'/app/{pk}/')

    api_key = getattr(settings, 'GROQ_API_KEY', None)
    if not api_key or not Groq:
        if is_ajax:
            return JsonResponse({'error': 'AI configuration missing.'}, status=500)
        messages.error(request, "AI configuration missing.")
        return redirect(f'/app/{pk}/')

    try:
        client = Groq(api_key=api_key)

        msgs = [
            {"role": "system", "content": f"""You are a career coach helping with a job application for {app.role} at {app.company}.
Notes: {app.notes}
Base Insight: {app.ai_suggestion}

IMPORTANT: Always respond using Markdown formatting. Use **bold** for key terms, numbered lists (1. 2. 3.) for steps or questions, bullet points (- ) for tips, and blank lines between paragraphs. Never write walls of text."""}
        ]

        for chat in app.ai_chat:
            msgs.append({"role": "user",      "content": chat['user']})
            msgs.append({"role": "assistant", "content": chat['ai']})

        msgs.append({"role": "user", "content": user_msg})

        completion = client.chat.completions.create(
            messages=msgs,
            model="llama-3.3-70b-versatile",
        )

        ai_reply = completion.choices[0].message.content

        history = list(app.ai_chat)
        history.append({'user': user_msg, 'ai': ai_reply})
        app.ai_chat = history
        app.save()

        logger.info("AI Chat reply sent — app ID: %d, User: '%s', message: '%.60s...'",
                    pk, request.user.username, user_msg)
        if is_ajax:
            return JsonResponse({'ai': ai_reply})

    except Exception as e:
        logger.error("AI Chat error — app ID: %d, User: '%s' — %s", pk, request.user.username, str(e))
        if is_ajax:
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f"AI Chat Error: {str(e)}")

    return redirect(f'/app/{pk}/')
