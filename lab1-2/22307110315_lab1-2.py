def vigenere_cipher(text, key, mode='encrypt'):
    result = ""
    key = key.upper()
    text = text.upper()
    key_length = len(key)
    
    # 过滤非字母字符（根据实验要求，通常只处理 A-Z）
    alpha_text = "".join(filter(str.isalpha, text))
    
    for i in range(len(alpha_text)):
        # 获取明文/密文和密钥对应的 0-25 整数 [cite: 44]
        char_code = ord(alpha_text[i]) - ord('A')
        key_code = ord(key[i % key_length]) - ord('A')
        
        if mode == 'encrypt':
            res_code = (char_code + key_code) % 26
        else:
            res_code = (char_code - key_code) % 26
            
        result += chr(res_code + ord('A'))
    return result

def main():
    # 1. 验证测试用例
    print("--- 验证测试用例 ---")
    test_p = "THEBASICOFCRYPTOGRAPHY"
    test_k1 = "SECURITY"
    print(f"加密验证: {vigenere_cipher(test_p, test_k1, 'encrypt')}") # 应输出 LLGVRABAGJELPXMMYVCJYG
    
    test_c = "YBHBNXCFOSHLBPGTAUACMS"
    test_k2 = "FUDAN"
    print(f"解密验证: {vigenere_cipher(test_c, test_k2, 'decrypt')}") # 应输出 THEBASICOFCRYPTOGRAPHY

    key_final = "CRYPTOGRAPHY"
    try:
        with open("lab1-2_input.txt", "r", encoding="utf-8") as f:
            ciphertext = f.read().strip()
        
        plaintext = vigenere_cipher(ciphertext, key_final, 'decrypt')
        
        with open("lab1-2_output.txt", "w", encoding="utf-8") as f:
            f.write(plaintext)
        
        print("\n--- 实验内容 2 ---")
        print(f"解密成功！结果已保存至 lab1-2_output.txt")
        print(f"内容预览: {plaintext[:50]}...")
    except FileNotFoundError:
        print("错误：未找到 lab1-2_input.txt 文件")

if __name__ == "__main__":
    main()