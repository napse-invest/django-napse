from django.db import models

from django_napse.core.models.bots.architecture import Architecture


class SinglePairArchitecture(Architecture):
    controller = models.ForeignKey("Controller", on_delete=models.CASCADE, related_name="single_pair_architectures")

    def __str__(self) -> str:
        return f"SINGLE PAIR ARCHITECHTURE {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Single Pair Architecture {self.pk}:\n"
        new_beacon = beacon + "\t"
        string += f"{beacon}Controller:\n{beacon}{self.controller.info(beacon=new_beacon, verbose=False)}\n"

        if verbose:  # pragma: no cover
            print(string)
        return string

    def copy(self):
        return SinglePairArchitecture.objects.create(
            controller=self.controller,
        )

    def list_controllers(self):
        return [self.controller]
