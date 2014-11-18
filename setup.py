from setuptools import setup

setup(name='MTBOStats',
      version='1.0',
      description='MTBO Statistic of world class races',
      author='Jiri Vrany',
      author_email='jiri.vrany@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
     install_requires=['Flask>=0.10.1', 'MySQL-python>=1.2.5', 'Flask-MySQL>=1.2'],
     )
