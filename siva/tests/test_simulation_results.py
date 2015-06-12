import pytest
import tempfile
import os

from siva.simulation.results import Results

def test_results():
    with tempfile.TemporaryDirectory() as work_dir:
        print(work_dir)


        with pytest.raises(OSError):
            results = Results(os.path.join(work_dir, 'results.hdf'),'r')

        with Results(os.path.join(work_dir, 'results.hdf'),'w') as results:
            assert results is not None

            results.select('tran')

            assert 'tran' in list(results.keys())

