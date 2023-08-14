from distutils.core import setup

setup(
    name="django-napse",  # How you named your package folder (MyLib)
    packages=["django-napse"],  # Chose the same as "name"
    version="1.4.0",  # Start with a small number and increase it with every change you make
    license="MIT",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="The heart and brains of the Napse Invest platform.",  # Give a short description about your library
    author="Napse Invest",  # Type in your name
    author_email="napse.invest@gmail.com",  # Type in your E-Mail
    url="https://github.com/napse-invest/django-napse",  # Provide either the link to your github or to your website
    download_url="https://github.com/napse-invest/django-napse/archive/v_01.tar.gz",  # I explain this later on
    keywords=["Investing", "Django", "Trading"],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        "django",
        "django-environ",
        "django-celery-beat",
        "psycopg2-binary",
        "celery",
        "redis",
        "python-binance",
        "shortuuid",
        "anybadge",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Programming Language :: Python :: 3.11",  # Specify which pyhton versions that you want to support
    ],
)
