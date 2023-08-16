from distutils.core import setup

# from setuptools import setup

setup(
    name="django-napse",
    packages=["django_napse"],
    version="{{VERSION}}",
    license="MIT",
    description="The heart and brains of the Napse Invest platform.",
    long_description="The heart and brains of the Napse Invest platform.",
    author="Napse Invest",
    author_email="napse.invest@gmail.com",
    url="https://github.com/napse-invest/django-napse",
    download_url="https://github.com/napse-invest/django-napse/archive/refs/tags/v1.4.0.tar.gz",
    keywords=["Investing", "Django", "Trading"],
    install_requires=[
        "django>=4.2",
        "django-environ>=0.10",
        "django-celery-beat>=2.5",
        "psycopg2-binary>=2.9",
        "celery>=5.3",
        "redis>=4.6",
        "python-binance>=1",
        "shortuuid>=1",
        "pandas>=2",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
)
