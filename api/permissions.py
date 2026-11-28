from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    message = "Само клиенти могат да извършват тази операция."

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.role == "client"
        )


class IsMaster(BasePermission):
    message = "Само майстори могат да извършват тази операция."

    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and request.user.role == "master"
        )
