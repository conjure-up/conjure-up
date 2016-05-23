import setuptools

# All these imported to be added to our distribution
import conjure
import maasclient  # noqa
import macumba  # noqa
import ubuntui  # noqa
import bundleplacer  # noqa


setuptools.setup(
    name="conjure-up",
    version=conjure.__version__,
    author="Adam Stokes",
    author_email="adam.stokes@ubuntu.com",
    description="Conjure for apt cloud packages",
    url="https://github.com/ubuntu-solutions-engineering/conjure-up",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "conjure-up = conjure.app:main",
            "conjure-craft = conjure.craft:main"
        ]
    }
)
