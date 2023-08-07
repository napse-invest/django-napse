from django.db import models

from django_napse.core.models.bots.architechture import Architechture


class SinglePairArchitechture(Architechture):
    controller = models.ForeignKey("Controller", on_delete=models.CASCADE, related_name="single_pair_architechtures")

    def __str__(self) -> str:
        return f"SINGLE PAIR ARCHITECHTURE {self.pk}"

    def info(self, verbose=True, beacon=""):
        string = ""
        string += f"{beacon}Single Pair Architechture {self.pk}:\n"
        new_beacon = beacon + "\t"
        string += f"{beacon}Controller:\n{beacon}{self.controller.info(beacon=new_beacon, verbose=False)}\n"

        if verbose:
            print(string)
        return string
