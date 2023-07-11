from django.urls import path

from .views import (
    create_user,
    get_customer,
    get_supplier,
    get_laboratory,
    send_supplier_form,
    get_lab_forms,
    update_form_status,
    get_verified_forms,
    customer_verification,
)
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path("create_user", create_user, name="user-create"),
    path("login", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("get_customer", get_customer, name="get_customer"),
    path("get_supplier", get_supplier, name="get_supplier"),
    path("get_laboratory", get_laboratory, name="get_laboratory"),
    path("send_supplier_form", send_supplier_form, name="send_supplier_form"),
    path("get_verified_forms", get_verified_forms, name="get_verified_forms"),
    path("get_lab_forms/<int:lab_id>", get_lab_forms, name="get_lab_forms"),
    path(
        "update_form_status/<int:lab_id>/<int:supplier_id>",
        update_form_status,
        name="update_form_status",
    ),
    path("customer_verification/<int:lab_id>/<int:supplier_id>", customer_verification, name="customer_verification"),
]
