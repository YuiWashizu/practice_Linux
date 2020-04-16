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