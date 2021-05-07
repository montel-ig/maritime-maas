from rest_framework.authtoken.models import Token


def token_authenticate(api_client, user):
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION="Bearer " + token.key)
    api_client.auth_user = user
    return api_client
