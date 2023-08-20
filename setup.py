from distutils.core import setup

from setuptools import find_packages

print(find_packages(exclude=["test", "test.*"]))
setup(
    name="django-napse",
    packages=find_packages(exclude=["test", "test.*"]),
    version="{{VERSION}}",
    license="MIT",
    description="The heart and brains of the Napse Invest platform.",
    long_description="The heart and brains of the Napse Invest platform.",
    author="Napse Invest",
    author_email="napse.invest@gmail.com",
    url="https://github.com/napse-invest/django-napse",
    download_url="https://github.com/napse-invest/django-napse/archive/refs/tags/v{{VERSION}}.tar.gz",
    keywords=["Investing", "Django", "Trading"],
    requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
