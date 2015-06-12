from distutils.core import setup
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='Siva',
    version='0.0.1',
    packages=['siva', 'siva.ui', 'siva.test', 'siva.icons', 'siva.tests', 'siva.tests.example_db_root',
              'siva.tests.example_db_root.lib_a', 'siva.tests.example_db_root.lib_a.cell_a',
              'siva.tests.example_db_root.lib_a.cell_b', 'siva.tests.example_db_root.lib_b',
              'siva.tests.example_db_root.lib_b.cell_a', 'siva.tests.example_db_root.lib_c', 'siva.types',
              'siva.types.test', 'siva.views', 'siva.canvas', 'siva.canvas.test', 'siva.design', 'siva.design.test',
              'siva.editors', 'siva.plotting', 'siva.plotting.test', 'siva.resources', 'siva.resources.test',
              'siva.utilities', 'siva.waveforms', 'siva.components', 'siva.components.test', 'siva.simulation',
              'siva.simulation.test', 'siva.simulation.spice', 'siva.design_database', 'siva.tool_integration',
              'siva.tool_integration.xyce', 'siva.tool_integration.pyqtgraph_plotting'],
    url='https://github.com/jasonpjacobs/Siva',
    license='BSD',
    author='Jason Jacobs',
    author_email='jason.jacobs@gmail.com',
    description='Circuit design using Python.',
    tests_require=['pytest'],
    install_requires=[
        'numpy>=1.9.2',
        'scipy>=0.15.0',
        'h5py>=2.3.1',
        'PySide>=1.2.1',
        'pandas>=0.15.2'
        ],
)
