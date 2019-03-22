from gestor_absencies.models import Worker, Team, Member


worker_attributes = {
    'first_name': 'first_name',
    'last_name': 'last_name',
    'email': 'email@example.com',
    'password': 'password'
}


def create_worker(username='username', is_admin=False):

    worker = Worker(
        first_name=worker_attributes['first_name'],
        last_name=worker_attributes['last_name'],
        email=worker_attributes['email'],
        username=username,
        password=worker_attributes['password'],
    )
    worker.set_password(worker_attributes['password'])
    worker.is_superuser = is_admin
    worker.save()
    return worker


def create_team(name='IT'):
    team = Team(
        name=name
    )
    team.save()
    return team


def create_member(worker, team):
    member = Member(
        worker=worker,
        team=team
    )
    member.save()
    return member
