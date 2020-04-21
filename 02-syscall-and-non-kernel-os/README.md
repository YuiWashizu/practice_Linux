# ユーザーモードで実現する機能
## システムコール
各種プロセスは、プロセス生成、ハードウェアの操作など、カーネルの助けが必要なときには、システムコールという手段によって、カーネルに処理を依頼する<br>

### システムコールの呼び出しの様子
#### 確認手順
 1. まずは、`hello.c`をコンパイルする。
    ```
    $ cc -o hello hello.c  #コンパイル
    $ ./hello
    hello. world
    $
    ```
 1. `strace`コマンドによって、どのようなシステムコールを発行するか調べる
    ```
    $ strace -o hello.log hello
    hello world
    $
    ```
 1. `hello.log`の中身を確認
    ```
    $ cat hello.log
    execve("./hello", ["./hello"], [/* 26 vars */]) = 0
    brk(NULL)                               = 0x25af000
    mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f968752a000
    access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
    open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
    fstat(3, {st_mode=S_IFREG|0644, st_size=85207, ...}) = 0
    mmap(NULL, 85207, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f9687515000
    close(3)                                = 0
    open("/lib64/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
    read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\20&\2\0\0\0\0\0"..., 832) = 832
    fstat(3, {st_mode=S_IFREG|0755, st_size=2156160, ...}) = 0
    mmap(NULL, 3985888, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f9686f3c000
    mprotect(0x7f96870ff000, 2097152, PROT_NONE) = 0
    mmap(0x7f96872ff000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1c3000) = 0x7f96872ff000
    mmap(0x7f9687305000, 16864, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f9687305000
    close(3)                                = 0
    mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f9687514000
    mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f9687512000
    arch_prctl(ARCH_SET_FS, 0x7f9687512740) = 0
    mprotect(0x7f96872ff000, 16384, PROT_READ) = 0
    mprotect(0x600000, 4096, PROT_READ)     = 0
    mprotect(0x7f968752b000, 4096, PROT_READ) = 0
    munmap(0x7f9687515000, 85207)           = 0
    fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(136, 0), ...}) = 0
    mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f9687529000
    write(1, "hello world\n", 12)           = 12
    exit_group(0)                           = ?
    +++ exited with 0 +++
    ```
 
 #### ここからわかること
`strace`の出力は、1つのシステムコール発行が1行に対応している。ここで、重要なのは、
```
 write(1, "hello world\n", 12)           = 12
```
であり、`write()`システムコールによって、`hello world\n`という文字列を画面出力していることがわかる。

## 実験
`sar`を使って、プロセスがユーザモードとカーネルモードのどちらで実行しているかの割合を確認することができる。

## システムコールの所要時間
`strace`に`-T`のオプションをつけると、各種システムコールの処理にかかった時間をマイクロ秒の精度で取得可能。`%system`が高い時に、具体的にどのシステムコールに時間がかかっているのかを確かめるために、この機能は便利に利用できる。
```
% strace -o -T hello_wtime´.log ./hello
execve("./hello", ["./hello"], [/* 26 vars */]) = 0 <0.006789>
brk(NULL)                               = 0x1407000 <0.000008>
mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f1181f22000 <0.000009>
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory) <0.000013>
open("/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3 <0.000013>
fstat(3, {st_mode=S_IFREG|0644, st_size=85207, ...}) = 0 <0.000009>
mmap(NULL, 85207, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f1181f0d000 <0.000010>
close(3)                                = 0 <0.000009>
open("/lib64/libc.so.6", O_RDONLY|O_CLOEXEC) = 3 <0.000024>
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0>\0\1\0\0\0\20&\2\0\0\0\0\0"..., 832) = 832 <0.000013>
fstat(3, {st_mode=S_IFREG|0755, st_size=2156160, ...}) = 0 <0.000011>
mmap(NULL, 3985888, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f1181934000 <0.000105>
mprotect(0x7f1181af7000, 2097152, PROT_NONE) = 0 <0.000018>
mmap(0x7f1181cf7000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1c3000) = 0x7f1181cf7000 <0.000017>
mmap(0x7f1181cfd000, 16864, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f1181cfd000 <0.000011>
close(3)                                = 0 <0.000008>
mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f1181f0c000 <0.000010>
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f1181f0a000 <0.000009>
arch_prctl(ARCH_SET_FS, 0x7f1181f0a740) = 0 <0.000009>
mprotect(0x7f1181cf7000, 16384, PROT_READ) = 0 <0.000013>
mprotect(0x600000, 4096, PROT_READ)     = 0 <0.000011>
mprotect(0x7f1181f23000, 4096, PROT_READ) = 0 <0.000014>
munmap(0x7f1181f0d000, 85207)           = 0 <0.000018>
fstat(1, {st_mode=S_IFCHR|0620, st_rdev=makedev(136, 0), ...}) = 0 <0.000010>
mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f1181f21000 <0.000010>
write(1, "hello world\n", 12)           = 12 <0.000124>
exit_group(0)                           = ?
+++ exited with 0 +++
```

## システムコールのラッパー関数
Linuxでは、プログラムの作成を助けるために、すべて、あるいは多くのプロセスに必要な様々なライブラリ関数が用意されている。<br>
システムコールは、通常の関数呼び出しとは違って、C言語などの高級言語から直接呼び出すことができない。アーキテクチャ依存のアセンブリコードを使って呼び出す必要がある。たとえば、x86_64アーキテクチャにおいて、getppid()システムコールは次のように発行する。
```
mov    $0x6e.%eax
syscall
```
普段アセンプリ言語を書く機会のない人は、ここではソースの詳しい意味を理解する必要はないが、明らかに普段自分が見ているソースとは別物であるという雰囲気だけを感じれればOK。<br>
もし、OSの助けがなければ、各プログラムはシステムコールを発行するたびにアーキテクチャ依存のアセンブリコードを書いて、高級言語からそれを呼び出さなくてはならない。<br>
これでは、プログラムの作成に手間がかかるし、別アーキテクチャへの移植性もない。これを解決するために、OSは、内部的にシステムコールを呼び出すだけのシステムコールのラッパーと呼ばれる一連の関数を提供している。ラッパー関数はアーキテクチャごとに存在する。高級言語で書かれたユーザプログラムからは、各言語に大して用意されているシステムコールのラッパー関数を呼び出すだけで済む。

## 標準Cライブラリ
C言語には、ISOによって定められた標準ライブラリがある。Linuxでも、この標準Cライブラリが提供されている。通常は、GNUプロジェクトが提供するglibcを標準Cライブラリとして使用する。C言語で書かれたほとんどの全てのCプログラムは、glibcをリンクしている。<br>
glibcは、システムコールのラッパー関数を含む。さらに、POSICという企画い定義されている関数も提供している。プログラムがどのようなライブラリをリンクしているかは、lddコマンドを用いて確かめられる。
```
$ ldd /bin/echo
  linux-vdso.so.1 =>  (0x00007ffd819cb000)
  libc.so.6 => /lib64/libc.so.6 (0x00007feeff871000)
  /lib64/ld-linux-x86-64.so.2 (0x00007feeffc3f000)
```
上記のうち、`libc`というのが標準Cライブラリを指す。python3の処理系であるpython3のコマンドについて確認する。
```
$ ldd /usr/bin/python3
  linux-vdso.so.1 =>  (0x00007ffe5c74f000)
  libpython3.6m.so.1.0 => /lib64/libpython3.6m.so.1.0 (0x00007faf90163000)
  libpthread.so.0 => /lib64/libpthread.so.0 (0x00007faf8ff47000)
  libdl.so.2 => /lib64/libdl.so.2 (0x00007faf8fd43000)
  libutil.so.1 => /lib64/libutil.so.1 (0x00007faf8fb40000)
  libm.so.6 => /lib64/libm.so.6 (0x00007faf8f83e000)
  libc.so.6 => /lib64/libc.so.6 (0x00007faf8f470000)
  /lib64/ld-linux-x86-64.so.2 (0x00007faf9068b000)
```
これについても、`libc`がリンクされていることがわかる。python3で書かれたスクリプトは、`python3`コマンドに与えれば直接実行できるが、`python3`コマンド自身は、内部的には標準Cライブラリを使っていることがわかる。最近では、普段C言語を直接使う人は少ないとおもうが、OSレベルでは、縁の下の力持ちとして、依然重要な前後であることがわかる。<br>
そのほかにも、システムに存在しているさまざまなプログラムに大して`ldd`コマンドを実行すると、その多くに`libc`がリンクされているのがわかる。