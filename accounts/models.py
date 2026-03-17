from django.db import models

# We use Django's built-in User model (django.contrib.auth.models.User).
# No custom models needed here — Django handles:
#   - username, email, first_name, last_name
#   - password stored as PBKDF2-SHA256 hash (never plain text)
#   - is_active, is_staff, is_superuser, last_login, date_joined
