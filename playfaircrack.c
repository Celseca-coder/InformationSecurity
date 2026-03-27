#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "scoreText.h"

#define TEMP 20
#define STEP 0.2
#define COUNT 10000

char *playfairDecipher(char *key, char *in,char *out, int len);
float playfairCrack(char *text,int len, char* maxKey);
static char *shuffleKey(char *in);

int main(int argc, char *argv[])
{
    // THINGS TO ENSURE: CIPHER AND KEY MUST BE UPPERCASE, CONSISTING ONLY OF LETTERS A-Z, AND NO OTHERS. YOU CAN SPELL OUT NUMBERS IF YOU NEED TO.
    // NEITHER THE CIPHER OR THE KEY SHOULD HAVE THE LETTER 'J' IN IT. IT WILL CRASH IF YOU DO NOT DO THESE THINGS. THIS IS A PROOF OF CONCEPT ONLY.
    char cipher[]  = "RIGAUNLPGNANYFPLHRZMUBDSLDLXTGCXGYOFQNTDGSKMKXPLHBRHAHOFLDLXEXNUPTSGFNEWHKDFSNHZOFXBHZLTPMIXLXYSOPGOLXEBNFPOFZGRSOHDPHTLLCXLHKHTOKTPTPNSMPPOBKNFSFISEOHRLDLXPSNFRMNSLTQFEIKBMPRONFARRBKCMDZTQETHFPHQGFUOLXDSELHZTLAGMKTPLEOPLTEIUGLOFMRLSDFAKIDQFNMKTPTHRLFYOFCYNSPTHKISNFVMHOGRHRFQGYKMXBSTOKZOOFHCAQOFGRYGFATGITOFMIFATHZCKBBNFMRLFLHOGLIZLEZTSFPLTPUMOFBSDSPOHZBGTPLTOKAHINZOGCGYPORDRLQZMZGDSTMDRHSDNPLXZOBDXLUHETBXIMNQKIFTMDVAFMSQMDXGANTLRLOFZOGRBKTZIMNFARDMHRINXLUHGTHRROLXPMHZBGTOKIPLXBPXDMRLZGLXHRDQDHNRIMTHNLFOUZBGXLBGITHDLEGYGEDQOPVGNFQUBOEBDMTMUNKMLEDPIOBGZKQLLEGYUYPLRHSDFASFISEOHRLDLXNFEDFLARIOLDHDBMDHLXOFCYLTLKHZBGRIGAUNLPOFNISLLEZOGCPLPOTGHMXBTDLGHZTHBXHDPTOFDPNFEGNFFRTLTIRGFXDSKIAQEKNFELTPOFHLRBSDPOTHTPIHPLAHNLZUZOBDXLUHBHIZLXAOHDSNRZZOLDHDNLNPBGBGYUPMISPLTMDHAULTELHPOFZOBDRLHRQSMPTHCGOFESLRGDRGFLDZ";
    int len = strlen(cipher);  
    char *out = malloc(sizeof(char)*(len+1));
    srand((unsigned)time(NULL)); // randomise the seed, so we get different results each time we run this program
    printf("Running playfaircrack, this could take a few minutes...\n");

    char key[] = "ABCDEFGHIKLMNOPQRSTUVWXYZ";
    int i=0;
    double score,maxscore=-99e99;
    // run until user kills it
    while(1){
        i++;
        score = playfairCrack(cipher,len,key);
        if(score > maxscore){
            maxscore = score;
            printf("best score so far: %f, on iteration %d\n",score,i);
            printf("    Key: '%s'\n",key);
            playfairDecipher(key, cipher,out, len);
            printf("    plaintext: '%s'\n",out);
        }
    }
    free(out);
    return 0;
}

void exchange2letters(char *key){
    int i = rand()%25;
    int j = rand()%25;
    char temp = key[i];
    key[i]= key[j];
    key[j] = temp;
}

void swap2rows(char *key){
    int i = rand()%5;
    int j = rand()%5;
    char temp;
    int k;
    for(k=0;k<5;k++){
        temp = key[i*5 + k];
        key[i*5 + k] = key[j*5 + k];
        key[j*5 + k] = temp;
    }
}

void swap2cols(char *key){
    int i = rand()%5;
    int j = rand()%5;
    char temp;
    int k;
    for(k=0;k<5;k++){
        temp = key[k*5 + i];
        key[k*5 + i] = key[k*5 + j];
        key[k*5 + j] = temp;
    }
}

/* key modification consists of several different modifications: swapping rows, cols, flipping the
   keysquare rows, flipping all cols and reversing the whole key. In addition to this, single letter
   swaps are made. The letter swaps occur ~90% of the time. */
void modifyKey(char *newKey,char *oldKey){
    int k,j,i = rand()%50;
    switch(i){
        case 0: strcpy(newKey,oldKey); swap2rows(newKey); break;
        case 1: strcpy(newKey,oldKey); swap2cols(newKey); break;       
        case 2: for(k=0;k<25;k++) newKey[k] = oldKey[24-k]; newKey[25] = '\0'; break; // reverse whole keysquare
        case 3: for(k=0;k<5;k++) for(j=0;j<5;j++) newKey[k*5 + j] = oldKey[(4-k)*5+j]; // swap rows up-down
                newKey[25] = '\0';
                break;
        case 4: for(k=0;k<5;k++) for(j=0;j<5;j++) newKey[j*5 + k] = oldKey[(4-j)*5+k]; // swap cols left-right
                newKey[25] = '\0';
                break;
        default:strcpy(newKey,oldKey); 
                exchange2letters(newKey);
    }
}

/* the function that implements the simulated annealing algorithm
   Input params:
     text: ciphertext
     len: length of text
     bestkey: initial key and store best key in iteration
   Output:
     return the best score in iteration
 */
float playfairCrack(char *text, int len, char *bestKey) {
    char *deciphered = malloc(sizeof(char) * (len + 1));
    char currentKey[26], nextKey[26];
    float currentScore, nextScore, maxScore;
    float T;
    int count;

    // 初始化：随机打乱当前密钥作为起点
    strcpy(currentKey, bestKey);
    shuffleKey(currentKey);
    
    playfairDecipher(currentKey, text, deciphered, len);
    currentScore = scoreTextQgram(deciphered, len);
    maxScore = currentScore;

    // 模拟退火主循环
    for (T = TEMP; T >= 0; T -= STEP) {
        for (count = 0; count < COUNT; count++) {
            modifyKey(nextKey, currentKey);
            playfairDecipher(nextKey, text, deciphered, len);
            nextScore = scoreTextQgram(deciphered, len);
            
            float dE = nextScore - currentScore;
            // 如果新密钥更好，或者在概率范围内允许变差
            if (dE > 0 || exp(dE / T) > (float)rand() / RAND_MAX) {
                currentScore = nextScore;
                strcpy(currentKey, nextKey);

                if (currentScore > maxScore) {
                    maxScore = currentScore;
                    strcpy(bestKey, currentKey);
                }
            }
        }
    }

    free(deciphered);
    return maxScore;
}

/* the function that implements decryption algorithm
    Input params:
      key: the key used for decryption
      text: ciphertext
      result: char array to store plaintext
      len: length of text
    Output:
      return result
*/
char *playfairDecipher(char *key, char *text, char *result, int len) {
    int i, a, b, r1, c1, r2, c2;
    for (i = 0; i < len; i += 2) {
        // 找到两个字符在 5x5 矩阵中的位置
        a = strchr(key, text[i]) - key;
        b = strchr(key, text[i + 1]) - key;
        r1 = a / 5; c1 = a % 5;
        r2 = b / 5; c2 = b % 5;

        if (r1 == r2) { // 同一行：向左循环移位
            result[i] = key[r1 * 5 + (c1 + 4) % 5];
            result[i + 1] = key[r2 * 5 + (c2 + 4) % 5];
        } else if (c1 == c2) { // 同一列：向上循环移位
            result[i] = key[((r1 + 4) % 5) * 5 + c1];
            result[i + 1] = key[((r2 + 4) % 5) * 5 + c2];
        } else { // 矩形对角
            result[i] = key[r1 * 5 + c2];
            result[i + 1] = key[r2 * 5 + c1];
        }
    }
    result[len] = '\0';
    return result;
}

// do fisher yeates shuffle      
static char *shuffleKey(char *in){
    int i,j;
    char temp;
    for (i = 24; i >= 1; i--){
        j = rand() % (i+1);
        temp = in[j];
        in[j] = in[i];
        in[i] = temp;
    }
    return in;
} 

