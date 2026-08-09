import re

with open(".github/workflows/build_esp32_firmware.yml", "r") as f:
    content = f.read()

replacement = """    - name: Build PlatformIO Project
      run: |
        cd firmware/esp32_bridge
        pio run

    - name: Merge Binaries
      run: |
        python -m pip install esptool
        cd firmware/esp32_bridge/.pio/build/esp32-s3-devkitc-1
        esptool.py --chip esp32s3 merge_bin -o merged-firmware.bin --flash_mode dio --flash_freq 80m --flash_size 4MB 0x0000 bootloader.bin 0x8000 partitions.bin 0x10000 firmware.bin

    - name: Upload Firmware Artifacts
      uses: actions/upload-artifact@v4
      with:
        name: esp32-s3-firmware
        path: |
          firmware/esp32_bridge/.pio/build/esp32-s3-devkitc-1/firmware.bin
          firmware/esp32_bridge/.pio/build/esp32-s3-devkitc-1/merged-firmware.bin"""

# Replace from "Build PlatformIO Project" to the end
start = content.find("    - name: Build PlatformIO Project")
if start != -1:
    content = content[:start] + replacement
    with open(".github/workflows/build_esp32_firmware.yml", "w") as f:
        f.write(content)
