import setuptools
import conjure


setuptools.setup(
    name="conjure",
    version=conjure.__version__,
    author="Adam Stokes",
    author_email="adam.stokes@ubuntu.com",
    description="Conjure for apt cloud packages",
    url="https://github.com/ubuntu-solutions-engineering/conjure",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "conjure-setup = conjure.app:main"
        ]
    },
    data_files=[
        ('share/man/man1', ['man/en/conjure-setup.1'])
    ],
    install_requires=open('requirements.txt', 'r').readlines()
)
