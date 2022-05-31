from setuptools import setup

setup(name='MTBOStats',
      version='1.2',
      description='MTBO Statistic of world class races',
      author='Jiri Vrany',
      author_email='jiri.vrany@gmail.com',
      url='https://github.com/jirivrany/stats_mtbo',
     install_requires=['Flask>=2.0.0', 'Flask-MySQL>=1.5.0', 'PyMySQL>=1.0.0'],
     )


