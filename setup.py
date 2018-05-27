from setuptools import setup, find_packages
setup(name="urpc", version="0.1.2",
      py_modules=['urpc'],
      url="http://github.com/bobuk/urpc",
      author="Grigory Bakunov",
      author_email='thebobuk@ya.ru',
      description='uRPC is oversimplistic RPC over Redis',
      install_requires=[
          'redis'
      ],
      scripts = ['scripts/urpc-cli'],
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],

)
