import setuptools

# All these imported to be added to our distribution
import conjureup
import maasclient  # noqa
import macumba  # noqa
import ubuntui  # noqa
import bundleplacer  # noqa


setuptools.setup(
    name="conjure-up",
    version=conjureup.__version__,
    author="Adam Stokes",
    author_email="adam.stokes@ubuntu.com",
    description="conjure-up a power tool for installing big software",
    url="https://github.com/ubuntu-solutions-engineering/conjure-up",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "conjure-up = conjureup.app:main",
            "conjure-craft = conjureup.craft:main"
        ]
    }
)
