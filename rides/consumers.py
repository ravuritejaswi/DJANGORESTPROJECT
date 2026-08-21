from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from rides.models import Ride
from urllib.parse import parse_qs
import json
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken


class RideConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def authenticate_user(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            User = get_user_model()
            return User.objects.get(id=user_id)

        except (TokenError, ObjectDoesNotExist, KeyError):
            return None
    @database_sync_to_async
    def check_ride_access(self, user):
        try:
            ride = Ride.objects.select_related(
                "user",
                "driver__user"
            ).get(id=self.ride_id)

            if ride.user_id == user.id:
                return True

            if ride.driver and ride.driver.user_id == user.id:
                return True

            return False

        except Ride.DoesNotExist:
            return False

    async def connect(self):
        self.ride_id = self.scope["url_route"]["kwargs"]["ride_id"]
        self.room_group_name = f"ride_{self.ride_id}"
        

        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)

        token = query_params.get("token", [None])[0]

        if not token:
            await self.close(code=4001)
            return

        user = await self.authenticate_user(token)

        if user is None:
            await self.close(code=4001)
            return

        has_access = await self.check_ride_access(user)

        if not has_access:
            await self.close(code=4003)
            return

        self.user = user

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, "room_group_name", None):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def ride_status(self, event):
        await self.send(
            text_data=json.dumps({
                "type": "ride_status",
                "ride_id": event["ride_id"],
                "status": event["status"],
            })
        )

    async def driver_location(self, event):
        await self.send(
            text_data=json.dumps({
                "type": "driver_location",
                "ride_id": event["ride_id"],
                "latitude": event["latitude"],
                "longitude": event["longitude"],
            })
        )