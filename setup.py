from setuptools import setup

setup(
    name='eschool',
    version='1.1',
    packages=['eschool'],
    package_dir={'eschool': 'eschool'},
    url='https://github.com/ennucore/eschool_py',
    license='MIT',
    author='ennucore',
    author_email='',
    install_requires=['requests'],
    description='Python library to work with Eschool electronic diary'
)
