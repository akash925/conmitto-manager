from factory import DjangoModelFactory
from api.personnel.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class NormalUserFactory(UserFactory):
    username = 'normaluser'
    password = 'normalpassword'
    email = 'user@email.com'
    first_name = 'John'
    last_name = 'Do®e'
