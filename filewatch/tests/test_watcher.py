import hashlib
import os
import time

from filewatch.watcher import Watcher
from filewatch.observer import ObserverBase
from filewatch.file_observer import file_updated_subject


class FileObserver(ObserverBase):
    def notify(self, *args, **kwargs):
        file_list = kwargs['file_list']
        assert len(file_list) == 1
        # There should always be two items, one is path second is meta
        assert len(file_list[0]) == 2

class FileObserverModification(ObserverBase):
    def notify(self, *args, **kwargs):
        file_list = kwargs['file_list']
        assert len(file_list) == 1
        file_list.pop(0)
        assert len(file_list) == 0


TEST_DIR = os.path.dirname(__file__)
TEST_DIR_A = os.path.join(TEST_DIR, 'TEST_DIR_A')

class TestWatcher(object):
    def test_file_discovory(self):
        """Are we able to find the correct number of files?"""
        watcher = Watcher()
        watcher.perform_check(TEST_DIR_A)

        assert len(watcher.files) == 5

    def test_observer_broadcasting(self):
        """Are our observers supplied with a list of modified files?"""
        file_updated_subject.remove_observers()
        file_updated_subject.register_observer(FileObserver())
        watcher = Watcher()
        watcher.perform_check(TEST_DIR_A)

        # "Touch" a file to update it's last modifed time
        a_file_path = os.path.join(TEST_DIR_A, "file_1")
        os.utime(a_file_path, None)

        watcher.perform_check(TEST_DIR_A)

    def test_filelist_modification(self):
        """Do we maintain integrity when observers modify our filelist?"""
        file_updated_subject.remove_observers()
        file_updated_subject.register_observer(FileObserverModification())
        file_updated_subject.register_observer(FileObserverModification())
        file_updated_subject.register_observer(FileObserverModification())

        watcher = Watcher()
        watcher.perform_check(TEST_DIR_A)

        # "Touch" a file to update it's last modifed time
        a_file_path = os.path.join(TEST_DIR_A, "file_1")
        key = a_file_path
        original_time = watcher.files[key]

        time.sleep(0.01)
        os.utime(a_file_path, None)

        watcher.perform_check(TEST_DIR_A)

        assert original_time < watcher.files[key]

    def test_default_directory(self):
        """What happens when no directory is supplied?"""
        watcher = Watcher()
        watcher.perform_check()

        assert len(watcher.files) > 0

    def test_deleting_file(self):
        """Do we track delted files?"""
        file_updated_subject.remove_observers()
        file_updated_subject.register_observer(FileObserver())

        new_file_path = os.path.join(TEST_DIR_A, "file_FOOBAR")
        with open(new_file_path, 'wb'):
            pass

        watcher = Watcher()
        watcher.perform_check(TEST_DIR_A)

        # Now delete the file and check again
        os.remove(new_file_path)
        watcher.perform_check(TEST_DIR_A)
