import setuptools

# All these imported to be added to our distribution
import conjureup
import maasclient  # noqa
import macumba  # noqa
import ubuntui  # noqa
import bundleplacer  # noqa

find_420_friendly_packages = setuptools.PEP420PackageFinder.find

setuptools.setup(
    name="conjure-up",
    version=conjureup.__version__,
    author="Adam Stokes",
    author_email="adam.stokes@ubuntu.com",
    description="conjure-up a power tool for installing big software",
    url="https://github.com/conjure-up/conjure-up",
    packages=find_420_friendly_packages(),
    entry_points={
        "console_scripts": [
            "conjure-up = conjureup.app:main"
        ]
    }
)
