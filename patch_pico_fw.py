import re

with open("firmware/pico_coprocessor/src/main.cpp", "r") as f:
    content = f.read()

# Remove setTX and setRX (default for Serial1 is 0 and 1 anyway)
content = content.replace("Serial1.setTX(ESP_TX_PIN);", "// Serial1.setTX(ESP_TX_PIN); // Not needed, default is GP0")
content = content.replace("Serial1.setRX(ESP_RX_PIN);", "// Serial1.setRX(ESP_RX_PIN); // Not needed, default is GP1")

# Remove setSDA and setSCL (default for Wire is 4 and 5)
content = content.replace("Wire.setSDA(I2C_SDA_PIN);", "// Wire.setSDA(I2C_SDA_PIN); // Not needed, default is GP4")
content = content.replace("Wire.setSCL(I2C_SCL_PIN);", "// Wire.setSCL(I2C_SCL_PIN); // Not needed, default is GP5")

# Remove analogWriteFreq (not supported on mbed core by default, PWM will run at default freq)
content = content.replace("analogWriteFreq(freq);", "// analogWriteFreq(freq); // Not supported in mbed core, using default frequency")

with open("firmware/pico_coprocessor/src/main.cpp", "w") as f:
    f.write(content)
