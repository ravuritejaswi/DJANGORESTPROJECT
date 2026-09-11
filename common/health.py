from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):

    def get(self, request):
        database_healthy = self.check_database()
        redis_healthy = self.check_redis()

        overall_healthy = database_healthy and redis_healthy

        response_data = {
            "status": "healthy" if overall_healthy else "unhealthy",
            "database": "healthy" if database_healthy else "unhealthy",
            "redis": "healthy" if redis_healthy else "unhealthy",
        }

        return JsonResponse(
            response_data,
            status=200 if overall_healthy else 503,
        )

    @staticmethod
    def check_database():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception:
            return False

    @staticmethod
    def check_redis():
        try:
            cache.set(
                "health_check",
                "ok",
                timeout=10,
            )

            value = cache.get("health_check")

            cache.delete("health_check")

            return value == "ok"

        except Exception:
            return False


class DatabaseHealthCheckView(View):

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            return JsonResponse({
                "status": "healthy",
                "service": "database",
            })

        except Exception:
            return JsonResponse(
                {
                    "status": "unhealthy",
                    "service": "database",
                },
                status=503,
            )


class RedisHealthCheckView(View):

    def get(self, request):
        try:
            cache.set(
                "health_check",
                "ok",
                timeout=10,
            )

            value = cache.get("health_check")

            cache.delete("health_check")

            if value == "ok":
                return JsonResponse({
                    "status": "healthy",
                    "service": "redis",
                })

            return JsonResponse(
                {
                    "status": "unhealthy",
                    "service": "redis",
                },
                status=503,
            )

        except Exception:
            return JsonResponse(
                {
                    "status": "unhealthy",
                    "service": "redis",
                },
                status=503,
            )