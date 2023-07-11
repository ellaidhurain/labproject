# views.py
from .models import Supplier, SupplierForm, Laboratory, Customer
from .serializers import (
    SupplierFormSerializer,
    SupplierSerializer,
    CustomerSerializer,
    LaboratoryFormSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import (
    permission_classes,
)
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.middleware.csrf import get_token


@api_view(["POST"])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
def login_user(request):
    # get user input
    username = request.data["username"]
    password = request.data["password"]

    # check if user exists and is active
    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {"detail": "Invalid username or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif not user.is_active:
        return Response(
            {"detail": "User is inactive"}, status=status.HTTP_400_BAD_REQUEST
        )

    # send payload to verify in decode
    payload = {
        "user": {
            "id": user.id,
            # "username":user.username,
            "exp": (datetime.utcnow() + timedelta(minutes=15)).isoformat(),
            "iat": datetime.utcnow().isoformat(),
        }
    }
    # generate JWT tokens
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    refresh_token = RefreshToken.for_user(user)
    # .
    # token = {"refresh": str(refresh_token), "access": access_token}

    # create response object
    response = Response({"message": "Login Success"}, status=status.HTTP_200_OK)
    # Set the CSRF token as a cookie
    csrf_token = get_token(request)
    response.set_cookie("csrftoken", csrf_token)
    response["Authorization"] = f"Bearer {access_token}"
    response["Refresh-Token"] = str(refresh_token)
    return response


# @func_token_required
@permission_classes((IsAuthenticated,))
# @user_type_required(allowed_user_types=["C"])
@api_view(["GET"])
def get_customer(request):
    try:
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data, status=200)
    except Customer.DoesNotExist:
        return Response(status=404)


# @func_token_required
@permission_classes((IsAuthenticated,))
# @user_type_required(allowed_user_types=["S"])
@api_view(["GET"])
def get_supplier(request):
    try:
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(
            suppliers, many=True, context={"request": request}
        )
        return Response(serializer.data, status=200)
    except Supplier.DoesNotExist:
        return Response(status=404)


# @func_token_required
@permission_classes((IsAuthenticated,))
# @user_type_required(allowed_user_types=["L"])
@api_view(["GET"])
def get_laboratory(request):
    try:
        laboratory = Laboratory.objects.all()
        serializer = LaboratoryFormSerializer(laboratory, many=True)
        return Response(serializer.data, status=200)
    except Laboratory.DoesNotExist:
        return Response(status=404)


# this will available in supplier page
# @func_token_required
@permission_classes((IsAuthenticated,))
# @user_type_required(allowed_user_types=["S"])
@api_view(["POST"])
def send_supplier_form(request):
    serializer = SupplierFormSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        response_data = {
            "id": serializer.data["id"],
            "supplier": serializer.data["supplier"],
            "laboratory": serializer.data["supplier"],
            "sub_name": serializer.data["sub_name"],
            "sub_address": serializer.data["sub_address"],
            "product_name": serializer.data["product_name"],
            "sub_proof": serializer.data["sub_proof_url"],
            "product_image": serializer.data["product_image_url"],
            "certificate_image": serializer.data["certificate_image_url"],
            "test_result_image": serializer.data["test_result_image_url"],
            "status": serializer.data["status"],
        }
        return Response(response_data, status=201)
    else:
        return Response(serializer.errors, status=400)


# this will available in lab page
# @func_token_required
@permission_classes((IsAuthenticated,))
# @user_type_required(allowed_user_types=["L"])
@api_view(["GET"])
def get_lab_forms(request, lab_id):
    if not lab_id:
        return Response({"error": "Missing 'id' parameter."}, status=400)

    try:
        lab = Laboratory.objects.get(id=lab_id)  # find lab id
        forms = SupplierForm.objects.filter(
            laboratory=lab, status="Pending"
        )  # get all forms sent to that lab_id

        serializer = SupplierFormSerializer(
            forms, many=True, context={"request": request}
        )  # returns an array of objects

        response_data = []
        for form_data in serializer.data:
            form = {
                "id": form_data["id"],
                "supplier": form_data["supplier"],
                "laboratory": form_data["laboratory"],
                "sub_name": form_data["sub_name"],
                "sub_address": form_data["sub_address"],
                "product_name": form_data["product_name"],
                "sub_proof": form_data["sub_proof_url"],
                "product_image": form_data["product_image_url"],
                "certificate_image": form_data["certificate_image_url"],
                "test_result_image": form_data["test_result_image_url"],
                "status": form_data["status"],
            }
            response_data.append(form)

        return Response(response_data, status=200)
    except Laboratory.DoesNotExist:
        return Response({"error": "Laboratory not found."}, status=404)


# this will updated by lab
# @func_token_required
@permission_classes((IsAuthenticated,))
# @user_type_required(allowed_user_types=["L"])
@api_view(["PUT"])
def update_form_status(request, lab_id, supplier_id):
    try:
        form = SupplierForm.objects.get(laboratory=lab_id, supplier=supplier_id)

        if form.status == "Verified":
            return Response(
                {"error": "Form is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if form.status == "Rejected":
            return Response(
                {"error": "Form is Rejected."}, status=status.HTTP_400_BAD_REQUEST
            )

        if form.status == "Pending":
            form.status = request.data.get("status")  # assign status = "Verified"
            form.test_result_image = request.data.get("test_result_image")
            form.save()
            serializer = SupplierFormSerializer(form, context={"request": request})
            response_data = {
                "id": serializer.data["id"],
                "supplier": serializer.data["supplier"],
                "laboratory": serializer.data["supplier"],
                "sub_name": serializer.data["sub_name"],
                "sub_address": serializer.data["sub_address"],
                "product_name": serializer.data["product_name"],
                "sub_proof": serializer.data["sub_proof_url"],
                "product_image": serializer.data["product_image_url"],
                "certificate_image": serializer.data["certificate_image_url"],
                "test_result_image": serializer.data["test_result_image_url"],
                "status": serializer.data["status"],
            }
        return Response(response_data, status=status.HTTP_200_OK)
    except SupplierForm.DoesNotExist:
        return Response({"error": "Form not found."}, status=status.HTTP_404_NOT_FOUND)


# this will available in customer page
# @func_token_required
@permission_classes((IsAuthenticated,))
# @user_type_required(allowed_user_types=["C"])
@api_view(["GET"])
def get_verified_forms(request):
    try:
        verified_forms = SupplierForm.objects.filter(status="Verified")
        if not verified_forms:
            return Response([], status=200)
        serializer = SupplierFormSerializer(verified_forms, many=True)
        return Response(serializer.data, status=200)
    except:
        return Response(status=400)


@permission_classes((IsAuthenticated,))
@api_view(["PUT"])
def customer_verification(request, id):
    try:
        form = SupplierForm.objects.get(id=id)
        is_verified_buyer = request.data["verified_buyer"]
        if is_verified_buyer == "True":
            form.verified_buyer = True
        else:
            form.verified_buyer = False

        form.save()
        serializer = SupplierFormSerializer(form, context={"request": request})
        response_data = {
            "id": serializer.data["id"],
            "supplier": serializer.data["supplier"],
            "laboratory": serializer.data["supplier"],
            "sub_name": serializer.data["sub_name"],
            "sub_address": serializer.data["sub_address"],
            "product_name": serializer.data["product_name"],
            "sub_proof": serializer.data["sub_proof_url"],
            "product_image": serializer.data["product_image_url"],
            "certificate_image": serializer.data["certificate_image_url"],
            "test_result_image": serializer.data["test_result_image_url"],
            "status": serializer.data["status"],
            "verified_buyer": serializer.data["verified_buyer"],
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except SupplierForm.DoesNotExist:
        return Response({"error": "Form not found."}, status=status.HTTP_404_NOT_FOUND)
