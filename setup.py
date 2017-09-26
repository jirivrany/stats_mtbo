from setuptools import setup

setup(name='MTBOStats',
      version='1.1',
      description='MTBO Statistic of world class races',
      author='Jiri Vrany',
      author_email='jiri.vrany@gmail.com',
      url='https://github.com/jirivrany/stats_mtbo',
     install_requires=['Flask==0.12.2', 'PyMySQL==0.7.11', 'Flask-MySQL==1.4.0'],
     )
