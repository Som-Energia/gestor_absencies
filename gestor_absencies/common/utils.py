from gestor_absencies.models import Worker


def jwt_response_token_user_id(token, user=None, request=None):
	user_id = Worker.objects.filter(username=request.data['username']).first().id
	return {
		'user_id': user_id,
		'token': token,
	}
