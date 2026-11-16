from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import LoginSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = serializer.validated_data
        return Response(
            {
                "details": "Login successful.",
                "data": {
                    "access": data["access"],
                    "refresh": data["refresh"],
                    "user": {
                        "id": data["user"].id,
                        "username": data["user"].username,
                        "role": data["user"].role,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "details": "User profile fetched successfully.",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "phone_number": user.phone_number,
                },
            },
            status=status.HTTP_200_OK,
        ) 