from setuptools import setup

setup(
    name='eschool',
    version='1.3.0',
    packages=['eschool'],
    package_dir={'eschool': 'eschool'},
    url='https://github.com/ennucore/eschool_py',
    license='MIT',
    author='ennucore',
    author_email='ennucore@gmail.com',
    install_requires=['requests'],
    description='Python library to work with Eschool electronic diary'
)
