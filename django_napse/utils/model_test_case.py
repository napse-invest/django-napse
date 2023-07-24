from django.test import TestCase


class ModelTestCase(TestCase):
    model = None

    def skip_condition(self):
        if self.__class__.__name__ == "ModelTestCase":
            return True
        return False

    def simple_create(self):
        error_msg = "You must define a simple_create method."
        raise NotImplementedError(error_msg)

    def test_setup(self):
        if self.skip_condition():
            return
        if self.model is None:
            error_msg = f"ModelTestCase subclass {self.__class__.__name__} must define a model attribute."
            raise NotImplementedError(error_msg)

    def test_simple_creation(self):
        if self.skip_condition():
            return
        instance = self.simple_create()
        if instance is None:
            error_msg = "simple_create method must return the created instance."
            raise ValueError(error_msg)

    def test_info(self):
        if self.skip_condition():
            return
        instance = self.simple_create()
        instance.info(verbose=True)

    def test_str(self):
        if self.skip_condition():
            return
        instance = self.simple_create()
        instance.__str__()
