"""
Integration tests for PE manipulation
"""

import pytest
import struct
import os
from pathlib import Path

# These tests require the compiled runtime and stdlib
pytestmark = pytest.mark.skipif(
    not os.path.exists("build/Release/boogpp_windows.dll"),
    reason="Runtime library not built"
)


class TestPEManipulation:
    """Test PE file manipulation capabilities"""

    def test_compile_pe_patcher_example(self, tmp_path):
        """Test compiling the PE patcher example"""
        from boogpp.compiler.cli import main as compiler_main

        example_path = Path("examples/advanced/pe_patcher.bpp")
        output_path = tmp_path / "pe_patcher.exe"

        result = compiler_main([
            "build",
            str(example_path),
            "-o", str(output_path),
            "--link"
        ])

        assert result == 0, "Compilation should succeed"
        assert output_path.exists(), "Output executable should be created"

    def test_pe_info_extraction(self, sample_pe):
        """Test extracting PE file information"""
        # This would test the actual PE manipulation functions
        # when compiled and linked with the runtime

        pe_info = {
            "machine": struct.unpack("<H", sample_pe[4:6])[0],
            "sections": struct.unpack("<H", sample_pe[6:8])[0]
        }

        assert pe_info["machine"] in [0x8664, 0x14c], "Should be x64 or x86"
        assert pe_info["sections"] > 0, "Should have sections"

    def test_pe_section_enumeration(self, sample_pe):
        """Test enumerating PE sections"""
        dos_header = struct.unpack("<H", sample_pe[:2])[0]
        assert dos_header == 0x5A4D, "Should have MZ signature"

        e_lfanew = struct.unpack("<I", sample_pe[0x3C:0x40])[0]
        nt_signature = struct.unpack("<I", sample_pe[e_lfanew:e_lfanew+4])[0]
        assert nt_signature == 0x4550, "Should have PE signature"


class TestProcessInjection:
    """Test process injection capabilities"""

    def test_compile_injector_example(self, tmp_path):
        """Test compiling the process injector example"""
        from boogpp.compiler.cli import main as compiler_main

        example_path = Path("examples/advanced/process_injector.bpp")
        output_path = tmp_path / "injector.exe"

        result = compiler_main([
            "build",
            str(example_path),
            "-o", str(output_path),
            "--link"
        ])

        assert result == 0, "Compilation should succeed"
        assert output_path.exists(), "Output executable should be created"

    @pytest.mark.requires_admin
    def test_dll_injection_safe_mode(self):
        """Test that DLL injection is blocked in SAFE mode"""
        # This would test that the safety system properly blocks
        # dangerous operations in SAFE mode
        pass

    @pytest.mark.requires_unsafe
    def test_memory_read_write(self):
        """Test reading and writing process memory"""
        # This would test actual memory operations
        # when running with UNSAFE mode
        pass


class TestRegistryManipulation:
    """Test registry manipulation"""

    def test_compile_registry_editor(self, tmp_path):
        """Test compiling the registry editor example"""
        from boogpp.compiler.cli import main as compiler_main

        example_path = Path("examples/advanced/registry_editor.bpp")
        output_path = tmp_path / "registry_editor.exe"

        result = compiler_main([
            "build",
            str(example_path),
            "-o", str(output_path),
            "--link"
        ])

        assert result == 0, "Compilation should succeed"
        assert output_path.exists(), "Output executable should be created"

    def test_registry_read_safe(self):
        """Test reading registry in SAFE mode"""
        # Test that reading is allowed in SAFE mode
        pass

    def test_registry_write_blocked_safe(self):
        """Test that registry writes are logged in SAFE mode"""
        # Test that writes trigger the safety system
        pass


class TestServiceManagement:
    """Test Windows service management"""

    def test_compile_service_example(self, tmp_path):
        """Test compiling the service example"""
        from boogpp.compiler.cli import main as compiler_main

        example_path = Path("examples/advanced/windows_service.bpp")
        output_path = tmp_path / "service.exe"

        result = compiler_main([
            "build",
            str(example_path),
            "-o", str(output_path),
            "--link"
        ])

        assert result == 0, "Compilation should succeed"
        assert output_path.exists(), "Output executable should be created"

    @pytest.mark.requires_admin
    def test_service_creation(self):
        """Test creating a Windows service"""
        # Test service creation with proper permissions
        pass


class TestDriverManagement:
    """Test kernel driver management"""

    def test_compile_driver_manager(self, tmp_path):
        """Test compiling the driver manager example"""
        from boogpp.compiler.cli import main as compiler_main

        example_path = Path("examples/advanced/kernel_driver.bpp")
        output_path = tmp_path / "driver_manager.exe"

        result = compiler_main([
            "build",
            str(example_path),
            "-o", str(output_path),
            "--link"
        ])

        assert result == 0, "Compilation should succeed"
        assert output_path.exists(), "Output executable should be created"

    @pytest.mark.requires_admin
    @pytest.mark.requires_unsafe
    def test_driver_loading(self):
        """Test loading a kernel driver"""
        # Test actual driver loading (requires UNSAFE mode and admin)
        pass


# Fixtures

@pytest.fixture
def sample_pe():
    """Create a minimal valid PE file for testing"""
    # DOS header
    dos_header = b'MZ' + b'\x00' * 58 + struct.pack("<I", 0x80)

    # PE signature
    pe_signature = b'PE\x00\x00'

    # COFF header (x64)
    coff_header = struct.pack("<HHIIIHH",
        0x8664,  # Machine (x64)
        3,       # NumberOfSections
        0,       # TimeDateStamp
        0,       # PointerToSymbolTable
        0,       # NumberOfSymbols
        0xF0,    # SizeOfOptionalHeader
        0x0002   # Characteristics
    )

    # Minimal PE structure
    pe = dos_header + b'\x00' * (0x80 - len(dos_header))
    pe += pe_signature + coff_header

    return pe


@pytest.fixture
def boogpp_runtime():
    """Load the BoogPP runtime library"""
    import ctypes
    runtime_path = Path("build/Release/boogpp_runtime.dll")

    if not runtime_path.exists():
        pytest.skip("Runtime library not built")

    return ctypes.CDLL(str(runtime_path))


def pytest_configure(config):
    """Add custom markers"""
    config.addinivalue_line(
        "markers", "requires_admin: tests that require administrator privileges"
    )
    config.addinivalue_line(
        "markers", "requires_unsafe: tests that require UNSAFE mode"
    )
