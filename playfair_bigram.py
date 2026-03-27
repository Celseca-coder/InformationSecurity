import collections
import itertools
import os

def count_bigrams(ciphertext):
    # 步骤一：统计密文双字母对频率
    bigrams = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    counter = collections.Counter(bigrams)
    return counter

def frequency_mapping(cipher_counter):
    # 步骤二：频率映射（展示密文最高频和英文最高频的对比）
    # 常见的英文双字母对（按一般统计频率排序）
    common_english_bigrams = ["TH", "HE", "IN", "ER", "AN", "RE", "ND", "AT", "ON", "NT"]
    
    print("=== 频率映射分析 ===")
    print(f"{'密文双字母对':<15} | {'出现次数':<10} | {'可能对应的英文双字母对 (假设)'}")
    print("-" * 55)
    
    top_cipher = cipher_counter.most_common(10)
    for i, (cipher_bg, count) in enumerate(top_cipher):
        eng_bg = common_english_bigrams[i] if i < len(common_english_bigrams) else "?"
        print(f"{cipher_bg:<15} | {count:<10} | {eng_bg}")
        
    return top_cipher

def get_possible_matrix_constraints(cipher_bg, plain_bg):
    """
    步骤三：利用 Playfair 规则推导相对几何位置关系（约束生成）
    C1, C2 = cipher_bg
    P1, P2 = plain_bg
    """
    C1, C2 = cipher_bg[0], cipher_bg[1]
    P1, P2 = plain_bg[0], plain_bg[1]
    
    constraints = []
    # 1. 矩形规则约束：C1 和 C2 与 P1 P2 分处矩形对角
    constraints.append(f"矩形规则: {P1}和{C2}同列, {P2}和{C1}同列; {P1}和{C1}同行, {P2}和{C2}同行")
    # 2. 同行规则约束：向右循环移位
    constraints.append(f"同行规则: {C1}在{P1}右侧相邻, {C2}在{P2}右侧相邻 (含绕回)")
    # 3. 同列规则约束：向下循环移位
    constraints.append(f"同列规则: {C1}在{P1}下方相邻, {C2}在{P2}下方相邻 (含绕回)")
    
    return constraints

# --- 新增：步骤四对应的“基于词典的暴力穷举 + 词频打分” ---

def generate_key_matrix(keyword):
    """基于关键字生成 5x5 的 Playfair 矩阵 (打平为 25 字符的字符串)"""
    keyword = keyword.upper().replace('J', 'I')
    matrix = []
    used = set()
    for char in keyword + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if char not in used and char.isalpha():
            matrix.append(char)
            used.add(char)
    return "".join(matrix)

def playfair_decipher(key, text):
    """使用指定的 key (25字符) 解密 Playfair 密文"""
    res = []
    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        if a not in key or b not in key:
            continue
            
        i1, i2 = key.index(a), key.index(b)
        r1, c1 = divmod(i1, 5)
        r2, c2 = divmod(i2, 5)
        
        if r1 == r2:     # 同行：向左循环移位 (解密是左移，加密是右移)
            res.append(key[r1*5 + (c1 - 1) % 5])
            res.append(key[r2*5 + (c2 - 1) % 5])
        elif c1 == c2:   # 同列：向上循环移位
            res.append(key[((r1 - 1) % 5)*5 + c1])
            res.append(key[((r2 - 1) % 5)*5 + c2])
        else:            # 矩形对角
            res.append(key[r1*5 + c2])
            res.append(key[r2*5 + c1])
    return "".join(res)

def score_text_by_bigrams(text):
    """简单的双字母词频打分系统 (类似模拟退火里的 n-gram)"""
    # 这里用常见的双字母频率作为基准分
    common_bigrams = {"TH": 10, "HE": 9, "IN": 8, "ER": 7, "AN": 6, "RE": 5, "ND": 4, "AT": 3, "ON": 2, "NT": 1}
    score = 0
    for i in range(len(text)-1):
        bg = text[i:i+2]
        if bg in common_bigrams:
            score += common_bigrams[bg]
    return score

def brute_force_dictionary_attack(ciphertext, dict_path="words.txt"):
    """使用词典文件进行暴力穷举，并通过词频分析找到正确结果"""
    print("\n=== 步骤四：暴力穷举 (Dictionary Attack) + 词频过滤 ===")
    if not os.path.exists(dict_path):
        print(f"找不到词典文件 {dict_path}，无法进行暴力穷举。")
        return
        
    print("正在读取词典并穷举所有关键字可能生成的矩阵...")
    best_score = -1
    best_keyword = ""
    best_plaintext = ""
    
    with open(dict_path, "r", encoding="utf-8") as f:
        words = f.read().splitlines()
        
    # 为了实验演示和应对可能的特定名词密钥，我们在词库中补充一些领域关键词
    extra_keywords = ["playfair", "fudan", "crypto", "security", "cipher", "hello"]
    for kw in extra_keywords:
        if kw not in words:
            words.append(kw)
        
    for word in words:
        if not word: continue
        # 1. 生成矩阵 (密钥)
        key_matrix = generate_key_matrix(word)
        
        # 2. 解密全文本进行评估以防局部无高频词
        sample_plaintext = playfair_decipher(key_matrix, ciphertext)
        
        # 3. 词频测分
        score = score_text_by_bigrams(sample_plaintext)
        
        if score > best_score:
            best_score = score
            best_keyword = word
            best_plaintext = playfair_decipher(key_matrix, ciphertext) # 全文解密
            
    print(f"穷举完成！尝试了 {len(words)} 个关键字。")
    print(f"==> 最佳关键字: {best_keyword.upper()}")
    print(f"==> 对应矩阵密钥: {generate_key_matrix(best_keyword)}")
    print(f"==> 最高词频得分: {best_score}")
    print(f"==> 前100字明文: {best_plaintext[:100]}...\n")

if __name__ == "__main__":
    # Playfaircrack.c 中的密文
    ciphertext = "RIGAUNLPGNANYFPLHRZMUBDSLDLXTGCXGYOFQNTDGSKMKXPLHBRHAHOFLDLXEXNUPTSGFNEWHKDFSNHZOFXBHZLTPMIXLXYSOPGOLXEBNFPOFZGRSOHDPHTLLCXLHKHTOKTPTPNSMPPOBKNFSFISEOHRLDLXPSNFRMNSLTQFEIKBMPRONFARRBKCMDZTQETHFPHQGFUOLXDSELHZTLAGMKTPLEOPLTEIUGLOFMRLSDFAKIDQFNMKTPTHRLFYOFCYNSPTHKISNFVMHOGRHRFQGYKMXBSTOKZOOFHCAQOFGRYGFATGITOFMIFATHZCKBBNFMRLFLHOGLIZLEZTSFPLTPUMOFBSDSPOHZBGTPLTOKAHINZOGCGYPORDRLQZMZGDSTMDRHSDNPLXZOBDXLUHETBXIMNQKIFTMDVAFMSQMDXGANTLRLOFZOGRBKTZIMNFARDMHRINXLUHGTHRROLXPMHZBGTOKIPLXBPXDMRLZGLXHRDQDHNRIMTHNLFOUZBGXLBGITHDLEGYGEDQOPVGNFQUBOEBDMTMUNKMLEDPIOBGZKQLLEGYUYPLRHSDFASFISEOHRLDLXNFEDFLARIOLDHDBMDHLXOFCYLTLKHZBGRIGAUNLPOFNISLLEZOGCPLPOTGHMXBTDLGHZTHBXHDPTOFDPNFEGNFFRTLTIRGFXDSKIAQEKNFELTPOFHLRBSDPOTHTPIHPLAHNLZUZOBDXLUHBHIZLXAOHDSNRZZOLDHDNLNPBGBGYUPMISPLTMDHAULTELHPOFZOBDRLHRQSMPTHCGOFESLRGDRGFLDZ"
    
    # 1. 统计频率
    cipher_counter = count_bigrams(ciphertext)
    
    # 2. 频率映射
    top_cipher = frequency_mapping(cipher_counter)
    
    # 3. 位置推导演示
    print("\n=== 位置推导与约束生成示例 ===")
    assumption_cipher = top_cipher[0][0]  # 假设最高频的密文对
    assumption_plain = "TH"               # 对应最高频的英文对
    print(f"如果我们假设密文 '{assumption_cipher}' 对应明文 '{assumption_plain}':")
    rules = get_possible_matrix_constraints(assumption_cipher, assumption_plain)
    for r in rules:
        print("  - " + r)
        
    print("\n[注]: 若要完全还原矩阵，可以通过生成假设矩阵并评估得分（步骤四）。")
    
    # 4. 基于词典进行暴力穷举并使用词频过滤找到最有可能的明文
    brute_force_dictionary_attack(ciphertext, dict_path="words.txt")