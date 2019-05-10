from gestor_absencies.models import Worker


def jwt_response_token_user_id(token, user=None, request=None):
	user = Worker.objects.filter(username=request.data['username']).first()
	return {
		'user_id': user.id,
		'is_admin': user.is_superuser,
		'token': token,
	}
