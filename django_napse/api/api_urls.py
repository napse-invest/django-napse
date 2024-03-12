import re
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, List

from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import GenericViewSet

if TYPE_CHECKING:
    from types import ModuleType


class ConflictingUrlNamesError(Exception):
    """When several viewset have the same automatic url."""


def build_main_router() -> DefaultRouter:
    """Create a main router object and register the appropriate viewsets to it based on the modules and classes found in the `api` directory.

    Returns:
        DefaultRouter: The main router object with registered URL patterns.
    """
    main_router = DefaultRouter()
    url_name_list: List[str] = []

    api_dir = Path(__file__).parent
    api_modules_folders_names = [folder.name for folder in api_dir.iterdir() if folder.is_dir() and not folder.name.startswith("_")]
    for module_name in api_modules_folders_names:
        try:
            module: ModuleType = import_module(f"django_napse.api.{module_name}.views")
        except (ImportError, ModuleNotFoundError) as error:
            print(f"Could not import module {module_name} ({type(error)})")
            print(error)
            continue
        for obj in vars(module).values():
            if isinstance(obj, type) and issubclass(obj, GenericViewSet):
                # from CamelCase to snake_case & remove "_view" (ex: MyWalletView -> my_wallet)
                url_name = re.sub(r"(?<!^)(?=[A-Z])", "_", obj.__name__).lower().replace("_view", "")

                if url_name in url_name_list:
                    error_msg: str = f"Url name {url_name} already exists"
                    raise ConflictingUrlNamesError(error_msg)
                main_router.register(url_name, obj, basename=url_name)
                url_name_list.append(url_name)

    return main_router


main_api_router = build_main_router()
