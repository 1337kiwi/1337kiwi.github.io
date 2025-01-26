output = 'D2C22A62DEA62CCE9EFA0ECC86CE9AFA4ECC6EFAC6162C3636CC76E6A6BE'

byteArr = bytes.fromhex(output)

revBytes = []

for byte in byteArr:
    reversedByte = 0
    for i in range(8):
        # Shift reversed_byte left by 1 and append the LSB of byte
        reversedByte = (reversedByte << 1) | (byte & 1)
        # Shift byte right by 1
        byte >>= 1
    revBytes.append(reversedByte)

reversed_string = bytes(revBytes).decode('ascii')

print(f"Reversed string: {reversed_string}")