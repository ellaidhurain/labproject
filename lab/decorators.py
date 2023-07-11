from functools import wraps
from django.conf import settings
from rest_framework import status
from django.http import JsonResponse
import jwt
from .models import User


def func_token_required(view_func):
    @wraps(view_func)
    def decorator(request, *args, **kwargs):
        # Get the JWT token from the Authorization header
        auth_header = request.headers.get("Authorization", "").split()
        if not auth_header or auth_header[0].lower() != "bearer":
            return JsonResponse(
                {"error": "Invalid token header. No credentials provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = auth_header[1]
        if not token:
            return JsonResponse(
                {"error": "Token not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Decode the JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload["user"]["id"]
            request.user = User.objects.get(id=user_id)
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"error": "Token has expired."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except (jwt.DecodeError, jwt.InvalidTokenError):
            return JsonResponse(
                {"error": "Invalid token."}, status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        return view_func(request, *args, **kwargs)

    return decorator


def user_type_required(allowed_user_types=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Authentication required."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if request.user.user_type not in allowed_user_types:
                return JsonResponse(
                    {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
