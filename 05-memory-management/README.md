# メモリ管理
Linuxはシステムに搭載されている全メモリを、カーネルのメモリ管理システムと呼ばれる機能によって管理している。メモリは各プロセスが使うのはもちろん、カーネル自身も使う。

## メモリに関する統計情報
 - `free`コマンド：システムが搭載するメモリ量と、使用中のメモリの量を得る

```
              total        used        free      shared  buff/cache   available
Mem:        1014672      741804       70996       15636      201872      100876
Swap:       1048572       27004     1021568
```

 - total : システムに搭載されている全メモリの量
 - free : 見かけ上の空きメモリ
 - buff/cache : バッファキャッシュ、およびページキャッシュが利用するメモリ
 - available : 実質的な空きメモリ
   - freeの値に空きメモリが足りなくなってきたら解放できるカーネル内メモリ領域のサイズを足したもの。解放できるメモリには、バッファキャッシュやページキャッシュの大部分およびその他カーネル内メモリの一部が含まれる

## Out Of Memory
メモリ使用量が増えてくると、空きメモリfreeが少なくなってくる。このような状態になると、カーネル内の解放可能なメモリ領域を解放する<br>
その後もメモリ使用量が増え続けると、システムはなをするにもメモリが足りず身動きが取れない「Out Of Memory」の状態になる。<br>
このような場合、メモリ管理システムには、適当なプロセスを選んで強制終了をすることによってメモリ領域を解放する「OOM killer」という機能がある。<br>
サーバにおいては、`sysctl`のvm.panic_on_oomパラメータをデフォルトの「0」(OOM killer発動)から「1」(OOM発生時にシステムを強制終了させる)に変更することがある


## 単純なメモリの割り当て
メモリ管理システムによるプロセスへのメモリ割り当てのしくみについて述べる。カーネルがプロセスにメモリを割り当てるのは、大きく分けて以下の2つのタイミングである
 - プロセス生成時
 - プロセス生成後、追加で動的メモリを割り当てる時

このうち、プロセス生成時のメモリ割り当てについては、Section3で説明済み（fork and exec）<br>

### 動的メモリの割り当て
プロセスが生成された後、さらに追加でメモリが必要になったら、プロセスはカーネルに対して、メモリ獲得用のシステムコールを発行することによって、メモリ割り当ての要求を出す。カーネルはメモリ割り当て要求がきたら、必要なサイズを空き容量から切り出して、その先頭アドレスを返す。このようなメモリの割り当て方法には、次のような問題がある
 - メモリの断片化
 - 別用途のメモリにアクセスできてしまう
 - マルチプロセスの扱いが困難

#### メモリの断片化
プロセスが生成された後に、メモリの獲得、解放を繰り返すと、メモリの断片化という問題が発生する。合計すれば大きなメモリ容量なのに、断片化されてしまっていること。複数の領域を一組として扱えば大丈夫と思われるかもしれないが、次のような理由によって、それが不可能
 - プログラムは、メモリ獲得のたびに、得られたメモリが何個の領域にまたがっているかを意識しなければならないので、非常に不便
 - サイズが100バイトより大きいひとかたまりのデータ、例えば300バイトの配列を作る用途には使えない
   - 配列は、同一型のデータを隙間を開けずに一列に並べたものだから

#### 別用途のメモリにアクセスできてしまう
プロセスは、カーネルや他のプロセスが使用しているアドレスを指定しさえすれば、それらの領域にアクセスできてしまう。データ漏洩や破壊のリスクがある。

#### マルチプロセスの扱いが困難
複数のプロセスを同時に動かす場合、同じプログラムをもう1つ起動し、メモリにマップしようとすると問題が発生する。なぜかというと、プログラムはコードに指定されているメモリのアドレスと、データに指定されているメモリのアドレスが値として定められているから。2つ以上の異なるプログラムを実行する場合でも、割り当て方式の場合は、各プログラムは、それぞれのプログラムが動作するアドレスが重ならないように気をつけて作る必要がある。

## 仮想記憶
 - 仮想記憶:システムに搭載されているメモリにプロセスから直接アクセスさせるのではなく、仮想アドレスというアドレスを用いて、関節的にアクセスさせるという方法
   - 仮想アドレス：プロセスから見えるアドレス
   - 物理アドレス：システムに搭載されているメモリの実際のアドレス
   - アドレス空間：アドレスによって可能な範囲

### ページテーブル
仮想アドレスから物理アドレスへの変換は、カーネルが使うメモリ内に保存されているページテーブルという表を用いる。仮想記憶において、すべてのメモリをページという単位で区切って管理している。ページのサイズはCPUのアーキテクチャごとに決められている。x86_64の場合は、4Kバイト

#### 実験：不正なアドレスにアクセスするプログラムを実際に作ってみる
 1. 「before invalid access」
 2. 必ずアクセスが失敗する「NULL」というアドレスに適当な値を書き込む
    - LinuxでNULLポインタを使用すると、確実に「segmentation fault」が起こる。なぜなら、NULLポインタへのアクセスを確実に検出するために、Linuxカーネルが意図的に仮想アドレスの最初の数ページをアクセス禁止にしている、つまり、物理アドレスを割り当てないでおくため
 3. 「after invalid access」

C言語などのメモリアドレスを直接扱える言語で作られたプログラムにおいては、そのプログラム自身、またはそれが使うライブラリに原因がある。一方、Pythonなどの、メモリアドレスを直接扱えない言語で作られたプログラムにおいては、問題は処理系、あるいはそれが使うライブラリにある

### プロセスへのメモリ割り当て
仮想記憶の仕組みによって、カーネルがどのようにプロセスにメモリを割り当てているのか、プロセス生成時、および生成後の追加割り当て時の、それぞれについて見てみる

#### プロセス生成時
プログラムの実行ファイルを読み出して、3章で説明した補足的な情報を読み出し、この領域を物理メモリ上に割り当てた上で、必要なデータをそこにコピーする。続いて、プロセスのためのページテーブルを作って、仮想アドレス空間と物理アドレス空間をマッピングする。

#### 追加割り当て時
プロセスが新規にメモリを要求すれば、カーネルは新規にメモリを割り当て、対応するページテーブルを作成した上で、割り当てたメモリに対応する仮想アドレスをプロセスに返す。

#### 実験
 1. プロセスのメモリマップ情報を表示
 1. メモリを新たに100Mバイト確保する
 1. 再度メモリマップ情報を表示する

```
実験に用いるソースコードは、
mmap(void* addr, size_t length, int prot, int flags, int fd, off_t offset):新しいマッピングを呼び出し、元プロセスの仮想アドレス空間に作成する
```

### 上位レイヤによるメモリ割り当て
C言語の標準ライブラリにある`malloc()`というメモリ獲得関数は、Linuxにおいて、内部にmmap()関数を呼び出している。`mmap()`はページ単位でメモリを獲得する一方で、`malloc()`はバイト単位で獲得する。バイト単位でのメモリ獲得を実現するために、glibcは、事前に`mmap()`システムコールによって、カーネルから大きなメモリ領域を獲得してプールし、プログラムからの`malloc()`関数発行時に、その領域から必要な量をバイト単位で切第sてプログラムに返すという処理をしている。プールしているメモリに空きがなくなれば、再度`mmap()`を発行して、新たなメモリ領域を獲得する。<br>
ちなみに、自分が使用しているメモリ量を報告する機能を持つプログラムがあるが、そのプログラムが出す値と、Linuxから見たプロセス使用メモリ量とが、異なることがよくある。これは、Linuxから見た使用量はプロセス生成時、および`mmap()`関数発行時において割り当てた全てのメモリの総計を指すのに対して、プログラムが報告する数値は、`malloc()`関数などによって獲得したバイト数の総計のみを指す。そのようなプログラムが報告する使用メモリ量が、具体的にどんな値を指しているのかは、それぞれのプログラムの仕様を確認する

## 問題の解決
### メモリの断片化
プロセスのページテーブルをうまく設定すれば、物理メモリ上では断片化している領域をプロセスの仮想アドレス空間上では大きな一つの領域として見せることができる

### 別用途のメモリにアクセスできてしまう
仮想アドレス空間は、プロセスごとに作られる。それに応じてページテーブルもプロセスごとに作成される。これによって、他のプロセスのメモリにはそもそもアクセスすることができなくなる。カーネルメモリについては、実装上の都合によって、実はすべてのプロセスの仮想アドレス空間にマップされている。ただし、カーネルのメモリに対応するページテーブルエントリについては、CPUがカーネルモードで実行している時にのみアクセスできる情報が付加されているため、ユーザモードでは破壊するなどは不可能

### マルチプロセスの扱いが困難
仮想アドレス空間はプロセスごとに存在する。そのため、各プログラムは他のプログラムとのアドレスの干渉を気にすることなく、それぞれ専用のアドレス空間で動作するようなプログラムを作ればよいのえ、自分用のメモリがどの物理アドレスに存在するかは、一切気にしなくて良い

## 仮想空間の応用
 - ファイルマップ
 - デマンドページング
 - コピーオンライト方式の高速なプロセス生成
 - スワップ
 - 階層型ページテーブル
 - ヒュー次ページ

### ファイルマップ
通常プロエスがファイルにアクセスするときは、ファイルを開いた時に`read()`, `write()`, `lseek()`システムコールを使う。これに加えてLinuxには、ファイルの領域を仮想アドレス空間場にメモリマップするするという機能がある。<br>
`mmap()`関数を所定の方法で呼び出すことで、ファイルの内容をメモリに読み出して、その領域を仮想アドレス空間にマップできる。マップしたファイルには、メモリアクセスと同じ方法でアクセスできる。アクセスした領域は、のちほど所定のタイミングで、ストレージデバイス上のファイルに書き戻される

### デマンドページング
プロセス生成時、その後の`mmap()`システムコールによってプロセスにメモリを割り当てる際は次のような手順をふむ
 1. カーネルが必要な領域を物理メモリ上に獲得する
 1. カーネルがページテーブルを設定し、仮想アドレス空間を物理アドレス空間に紐づける

しかし、この方法では、メモリを無駄に消費するという問題点がある。獲得したメモリの中には次のようにメモリを獲得してから当分あるいはプロセス終了まで使わない領域が存在するため
 - 大きなプログラムの中の実行中に使われなかった機能のためのコード領域やデータ領域
 - glibcが確保したメモリプールのうち、ユーザが`malloc()`関数で確保しなかった部分

このような問題を解決するために、Linuxはデマンドページングという仕組みを使って、メモリをプロセスに割り当てていく。デマンドページングにおいては、プロセスの仮想アドレス空間内の各ページに対応する物理メモリは、当該ページに最初にアクセスした時に割り当てる。

#### デマンドページングの実験
#### 実験より考察
 - メモリ領域を獲得しても、その領域に実際にアクセスするまではシステムの物理メモリ使用量はほぼ変化しない
 - メモリアクセスが始まってからは、秒間10Mバイト程度、メモリ使用量が増加する
 - メモリアクセス終了後は、メモリ使用量が変わらない
 - プロセスが終了すると、メモリ使用量はプロセス開始前の状態に戻る
 - メモリ領域を獲得してからアクセスするまでは、仮想メモリの使用量が約100Mバイト増えるが、物理使用量は変わらない
 - メモリアクセスによって物理メモリ使用量は毎秒10Mバイトほど増えるが、仮想メモリ使用量は増えない
 - メモリアクセス終了後の物理メモリメモリ獲得前より約100Mバイト多い

#### 仮想メモリの枯渇と物理メモリの枯渇
プロセスの実行中に、メモリ獲得に失敗して以上終了することがあるが、これについては仮想メモリの枯渇と物理メモリの枯渇という2種類がある。<br>
 - 仮想メモリの枯渇：プロセスが仮想アドレス空間の範囲いっぱいまで仮想メモリを使い切った状態でメモリを獲得しようとした時に発生する。
 - 物理メモリの枯渇：システムに搭載されている物理メモリがなくなる状態

### コピーオンライト
プロセス生成に使う`fork()`システムコールも、仮想記憶の仕組みを使って高速化されている。<br>
`fork()`システムコール発行時には、親プロセスのメモリを子プロセスにすべてコピーするのではなく、ページテーブルだけをコピーする。ページテーブルのエントリ内には、書き込み権限を示すフィールドがあるが、このときも親も子も、全ページ書き込み権限を無効化する。<br>
その後、親プロセスまたは子プロセスのどちらかがページのどこかを更新しようとすると、次のような流れで共有を解除する。
 1. ページの書き込みは許されていないため、書き込み時にCPU上でページフォルトが発生
 1. CPUがカーネルモードに遷移し、カーネルのページフォルトハンドラが動作
 1. ページフォルトハンドラは、アクセスされたページを別の場所にコピーして、書き込みしようとしたプロセスに割り当てたうえで内容を書き換える
 1. 親プロセス子プロセスそれぞれについて、共有が解除されたページに対応するページテーブルエントリを更新する

#### 実験
 1. 100Mバイトのメモリを獲得して、全てのページにアクセス
 1. システムのメモリ使用量を確認する
 1. `fork()`システムコールを発行
 1. 親プロセスと子プロセスはそれぞれ次のような動きをする
    - 親プロセス
      1. 子プロセスの終了を待つ 
    - 子プロセス
      1. システムのメモリ使用量、および自身の仮想メモリ使用量、物理メモリ使用量、メジャーフォルトの回数、マイナーフォルトの回数を表示
      1. 1.において獲得した領域のすべてのページにアクセス
      1. システムのメモリ使用量、および自身の仮想メモリ使用量、物理メモリの使用量、メジャーフォルトの回数、マイナーフォルトの回数を表示

#### 実験より考察
 - 親プロセスのメモリ使用量は100Mバイトを超えるのに、`fork()`システムコールを実行後、かつ子プロセスによるメモリアクセス前のメモリ使用量は数百Kバイトしか増えていない
 - 子プロセスによるメモリアクセス後にはページフォルトの数が増えており、かつ、システムのメモリ使用量が100Mバイト増えている

個々のプロセスの物理メモリ使用量について<br>
親プロセスと子プロセスで共有されているメモリはそれぞれのプロセスにおいて二重計上される、このため、すべてのプロセスの物理メモリ使用量を合計すると、全プロセスが実際に使用しているメモリ量よりも多くなるので、注意が必要<br>

## swap
物理メモリがなくなると、OOMという状態になると説明した。しかし、実際には仮想記憶の仕組みを応用したスワップと呼ばれる、OOMに対する救済措置の機能がLinuxにはある。<br>
 - スワップ：ストレージデバイスの一部を一時的にメモリの代わりとして使用する仕組み

## 階層型ページテーブル
x86_64アーキテクチャにおいて、仮想アドレス空間の大きさは128Tバイトで、1ページの大きさは4Kバイト、ページテーブルエントリのサイズは8バイト。ここから、プロセス1つあたりのページテーブルに256Gバイトという巨大なメモリが必要になる

## ヒュージページ
プロセスの仮想メモリ使用サイズが増えてくると、それに伴って、当該プロセスのページテーブルに使用する物理メモリ量が増えていく。このような場合は、メモリ使用量の増加だけでなく、`fork()`システムコールも遅くなるという問題が発生する。なぜなら、`fork()`システムコールは、コピーオンライトによるメモリ割り当てによって親プロセスが使用している物理メモリはコピーしないが、ページテーブルは、親プロセスと同じサイズのものを新規作成するためである。この問題を解決するために、Linuxには、「ヒュージページ」という仕組みがある。<br>
 - ヒュージページ：通常より大きなサイズのページ。メモリ量をたくさん使うプロセスについて、ページテーブルに必要なメモリ量が削減できる

### ヒュージページの使い方
`mmap()`関数の`flags`引数に`MAP_HUGETLB`フラグを与えることで、ヒュージページを獲得する。しかし、実際には、プログラムから直接ヒュージページを獲得するよりは、既存プログラムのヒュージページ利用設定を有効化する、という使い方の方が多い<br>
データベースや仮想マシンマネージャなど、仮想メモリを大量に使うソフトウェアには、ヒュージページを使う設定が用意されていることがある。

### トランスペアレントヒュージページ
 - トランスペアレントヒュージページ：これは仮想アドレス空間内の連続する複数の4Kバイトページが所定の条件を満たせばそれらをまとめて自動的にヒュージページにしてくれれうもの