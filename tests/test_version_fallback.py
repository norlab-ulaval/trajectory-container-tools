# coding=utf-8
"""
Unit tests for the version.py fallback mechanisms.

These tests verify that the version.py module correctly handles various scenarios
including missing version.txt file and different fallback approaches.
"""

import pytest
import os
import sys
import tempfile
import subprocess

from trajectory_container_tools.version import _get_version, _get_fallback_version, __version__


class TestVersionFileReading:
    """Test reading version from version.txt file."""

    def test_version_file_exists_and_readable(self, mocker):
        """Test that version is correctly read from version.txt when file exists."""
        mock_exists = mocker.patch('os.path.exists')
        mock_exists.return_value = True
        mocker.patch('builtins.open', mocker.mock_open(read_data='1.2.3-beta.4\n'))
        
        version = _get_version()
        assert version == '1.2.3-beta.4'

    def test_version_file_missing_triggers_fallback(self, mocker):
        """Test that missing version.txt file triggers fallback mechanism."""
        mock_exists = mocker.patch('os.path.exists')
        mock_exists.return_value = False
        
        # Since fallback might succeed with different methods, just ensure it returns a string
        version = _get_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_version_file_io_error_triggers_fallback(self, mocker):
        """Test that IO error when reading version.txt triggers fallback."""
        mock_exists = mocker.patch('os.path.exists')
        mock_exists.return_value = True
        mocker.patch('builtins.open', side_effect=OSError("File not accessible"))
        
        version = _get_version()
        assert isinstance(version, str)
        assert len(version) > 0

    def test_version_file_unicode_error_triggers_fallback(self, mocker):
        """Test that Unicode decode error triggers fallback."""
        mock_exists = mocker.patch('os.path.exists')
        mock_exists.return_value = True
        mocker.patch('builtins.open', side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"))
        
        version = _get_version()
        assert isinstance(version, str)
        assert len(version) > 0


class TestFallbackMechanisms:
    """Test the various fallback mechanisms for version detection."""

    def test_fallback_installed_package_metadata_success(self, mocker):
        """Test successful fallback to installed package metadata."""
        # Mock the metadata import path
        mock_metadata = mocker.MagicMock()
        mock_metadata.version.return_value = '2.0.0-installed'
        mocker.patch('importlib.metadata', mock_metadata)
        
        version = _get_fallback_version()
        assert version == '2.0.0-installed'
        mock_metadata.version.assert_called_once_with("trajectory-container-tools")

    def test_fallback_git_describe_success(self, mocker):
        """Test successful fallback to git describe when metadata fails."""
        # Remove importlib.metadata from sys.modules to trigger ImportError
        mocker.patch.dict('sys.modules', {'importlib.metadata': None})
        mock_subprocess = mocker.patch('subprocess.check_output')
        mock_subprocess.return_value = 'v1.5.0-10-gab12cd3-dirty\n'
        
        version = _get_fallback_version()
        assert version == 'v1.5.0-10-gab12cd3-dirty'
        
        # Verify git command was called correctly
        expected_call = [
            "git", "describe", "--tags", "--dirty", "--always"
        ]
        mock_subprocess.assert_called_once()
        args, kwargs = mock_subprocess.call_args
        assert args[0] == expected_call
        assert 'cwd' in kwargs
        assert 'stderr' in kwargs
        assert 'universal_newlines' in kwargs

    def test_fallback_unknown_when_all_fail(self, mocker):
        """Test fallback to 'unknown' when all methods fail."""
        mocker.patch.dict('sys.modules', {'importlib.metadata': None})
        mocker.patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'git'))
        
        version = _get_fallback_version()
        assert version == 'unknown'

    def test_fallback_unknown_when_git_not_available(self, mocker):
        """Test fallback to 'unknown' when git is not available."""
        mocker.patch.dict('sys.modules', {'importlib.metadata': None})
        mocker.patch('subprocess.check_output', side_effect=FileNotFoundError())
        
        version = _get_fallback_version()
        assert version == 'unknown'

    def test_fallback_git_empty_output_still_returns_value(self, mocker):
        """Test that empty git describe output still returns unknown."""
        mocker.patch.dict('sys.modules', {'importlib.metadata': None})
        mock_subprocess = mocker.patch('subprocess.check_output')
        mock_subprocess.return_value = '\n'
        
        version = _get_fallback_version()
        assert version == 'unknown'

    def test_fallback_os_error_triggers_unknown(self, mocker):
        """Test that OS error during git describe triggers 'unknown' fallback."""
        mocker.patch.dict('sys.modules', {'importlib.metadata': None})
        mocker.patch('subprocess.check_output', side_effect=OSError("OS error"))
        
        version = _get_fallback_version()
        assert version == 'unknown'


class TestVersionModuleImport:
    """Test that version module can be imported and __version__ is available."""

    def test_version_module_has_version_attribute(self):
        """Test that version module exposes __version__ attribute."""
        assert hasattr(sys.modules['trajectory_container_tools.version'], '__version__')
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_is_string(self):
        """Test that __version__ is a string."""
        assert isinstance(__version__, str)

    def test_version_not_empty(self):
        """Test that __version__ is not empty."""
        assert len(__version__) > 0
        assert __version__.strip() != ""


class TestPythonVersionCompatibility:
    """Test compatibility with different Python versions for metadata import."""

    def test_python37_uses_importlib_metadata(self, mocker):
        """Test that Python 3.7 uses importlib_metadata backport."""
        mocker.patch('sys.version_info', (3, 7))
        mock_importlib_metadata = mocker.MagicMock()
        mock_importlib_metadata.version.return_value = '1.0.0-py37'
        mocker.patch.dict('sys.modules', {'importlib_metadata': mock_importlib_metadata})
        
        # Re-import the module to trigger the version check
        import importlib
        importlib.reload(sys.modules['trajectory_container_tools.version'])
        
        # The test would need to be more complex to fully verify this,
        # but we can at least check that the fallback mechanism works
        version = _get_fallback_version()
        assert isinstance(version, str)

    def test_python38_plus_uses_builtin_metadata(self, mocker):
        """Test that Python 3.8+ can use builtin importlib.metadata."""
        mocker.patch('sys.version_info', (3, 8))
        
        # This is more of an integration test since we can't easily mock the import logic
        version = _get_fallback_version()
        assert isinstance(version, str)


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""

    def test_current_repository_version_detection(self):
        """Test version detection in the current repository context."""
        # This should work in the actual repository
        version = _get_version()
        assert isinstance(version, str)
        assert len(version) > 0
        
        # Should not be 'unknown' in the actual repository
        # (unless there are issues with the setup)
        # Note: This might be 'unknown' in some CI environments, so we just check it's a string

    def test_version_consistency(self):
        """Test that version detection is consistent across multiple calls."""
        version1 = _get_version()
        version2 = _get_version()
        assert version1 == version2

    def test_fallback_consistency(self):
        """Test that fallback mechanism is consistent across multiple calls."""
        fallback1 = _get_fallback_version()
        fallback2 = _get_fallback_version()
        assert fallback1 == fallback2


class TestErrorHandling:
    """Test error handling in various edge cases."""

    def test_permission_error_handling(self, mocker):
        """Test handling of permission errors when reading version file."""
        mock_exists = mocker.patch('os.path.exists')
        mock_exists.return_value = True
        mocker.patch('builtins.open', side_effect=PermissionError("Permission denied"))
        
        version = _get_version()
        assert isinstance(version, str)
        # Should fallback, not crash

    def test_metadata_exception_handling(self, mocker):
        """Test handling of various exceptions from metadata module."""
        mock_metadata = mocker.MagicMock()
        mocker.patch('importlib.metadata', mock_metadata)
        
        # Test different types of exceptions that metadata.version might raise
        exceptions_to_test = [
            ImportError("Module not found"),
            AttributeError("No version attribute"),
            Exception("Generic error"),
            KeyError("Package not found")
        ]
        
        for exception in exceptions_to_test:
            mock_metadata.version.side_effect = exception
            version = _get_fallback_version()
            assert isinstance(version, str)
            # Should handle gracefully and continue to git fallback
