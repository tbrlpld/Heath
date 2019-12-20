from .base import BaseTest, dummy_request


class TestMyViewSuccessCondition(BaseTest):

    def setUp(self):
        super(TestMyViewSuccessCondition, self).setUp()
        self.init_database()

        from heath.models import MyModel

        model = MyModel(name='one', value=55)
        self.session.add(model)

    def test_passing_view(self):
        from heath.views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info['one'].name, 'one')
        self.assertEqual(info['project'], 'heath')


class TestMyViewFailureCondition(BaseTest):

    def test_failing_view(self):
        from heath.views.default import my_view
        info = my_view(dummy_request(self.session))
        self.assertEqual(info.status_int, 500)
