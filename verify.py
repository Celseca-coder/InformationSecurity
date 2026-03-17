import hashlib

hash_answer = '77eb452f0f9310186dc6d3e562ab400e'


# 用于验证待确认明文，请确保明文中包含分割重复字符的‘X’
def verify(plain_text: str):
    return hashlib.md5(plain_text.encode(encoding='UTF-8')).hexdigest() == hash_answer
if __name__ == "__main__":
    print("Please parse the plaintext (without quotes):")
    # 接收输入并去除可能存在的空白符和引号
    user_input = input().strip().replace("'", "")
    
    if verify(user_input):
        print("Verification Successful! The plaintext is correct.")
    else:
        print("Verification Failed. Hash does not match.")