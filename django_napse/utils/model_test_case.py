from django_napse.utils.custom_test_case import CustomTestCase


class ModelTestCase(CustomTestCase):
    model = None
    exchange = None

    def simple_create(self):
        error_msg = "You must define a simple_create method."
        raise NotImplementedError(error_msg)

    def test_setup(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        if self.model is None:
            error_msg = f"ModelTestCase subclass {self.__class__.__name__} must define a model attribute."
            raise NotImplementedError(error_msg)

    def test_simple_creation(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        instance = self.simple_create()
        if instance is None:
            error_msg = "simple_create method must return the created instance."
            raise ValueError(error_msg)

    def test_info(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        instance = self.simple_create()
        instance.info(verbose=False)

    def test_str(self):
        skip, reason = self.skip_condition()
        if skip:
            self.skipTest(reason)
        instance = self.simple_create()
        instance.__str__()
