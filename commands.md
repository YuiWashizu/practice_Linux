# 今回使用したコマンド一覧

|command|使い方||
|:-:|:-:|:-:|
|strace|`strace <command>`| `<command>`が使用するシステムコールおよび受け取るシグナルを確認できる|
|taskset|`taskset -c <int> <program>`| `<program>`を指定した`<int>`番の論理CPUのみで実行すること|
