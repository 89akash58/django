from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from .models import SalesData, CategoryData
from datetime import datetime, timedelta
import random
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.contrib.auth.models import User
from rest_framework import status

def generate_dummy_sales_data():
    SalesData.objects.all().delete()  # Clear existing data
    start_date = datetime.now().date() - timedelta(days=30)
    for i in range(30):
        date = start_date + timedelta(days=i)
        SalesData.objects.create(date=date, sales=random.randint(100, 1000))

def generate_dummy_category_data():
    CategoryData.objects.all().delete()  # Clear existing data
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Toys']
    for category in categories:
        CategoryData.objects.create(category=category, value=random.randint(1000, 5000))

@csrf_exempt
def sales_data(request):
    if SalesData.objects.count() == 0:
        generate_dummy_sales_data()
    data = list(SalesData.objects.values('date', 'sales').order_by('date'))
    return JsonResponse(data, safe=False)

@csrf_exempt
def category_data(request):
    if CategoryData.objects.count() == 0:
        generate_dummy_category_data()
    data = list(CategoryData.objects.values('category', 'value'))
    return JsonResponse(data, safe=False)

@csrf_exempt
def scatter_data(request):
    data = [{'x': random.randint(0, 100), 'y': random.randint(0, 100)} for _ in range(50)]
    return JsonResponse(data, safe=False)


@csrf_exempt  # Disable CSRF if using Postman or for APIs
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Print received data for debugging

            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if not name or not email or not password or not confirm_password:
                return JsonResponse({"error": "All fields are required"}, status=400)

            if password != confirm_password:
                return JsonResponse({"error": "Passwords do not match"}, status=400)

            if User.objects.filter(username=email).exists():
                return JsonResponse({'error': 'User already exists'}, status=400)

            user = User.objects.create(
                username=email,
                email=email,
                first_name=name,
                password=make_password(password)
            )
            print("User created:", user)  # Print confirmation of user creation
            return JsonResponse({'message': 'User registered successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        except Exception as e:
            print(f"Error during user registration: {e}")  # Log error in console
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_all(request):
    if request.method == 'GET':
        users = User.objects.all().values('id','username', 'email', 'first_name','password')
        user_list=list(users)
        return JsonResponse(user_list, safe= False ,status=200)
    
    return JsonResponse({'message':"Invalid request"}, status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)  # Print received data for debugging
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return JsonResponse({"error": "All fields are required"}, status=400)
            
            user = authenticate(username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return JsonResponse({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'message': "Login successful"
                }, status=200)
            else:
                return JsonResponse({'error': "Invalid credentials"}, status=401)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid json data'}, status=400)
        except Exception as e:
            print(f"Error during login: {e}")  # Log error in console
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    return JsonResponse({'message': 'Invalid request method'}, status=405)
            

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def update_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response({"error": "Both old and new passwords are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the old password is correct
    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the new password is valid and set it
    user.set_password(new_password)
    user.save()
    
    return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)