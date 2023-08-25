# Owl🦉

A dependency module feature scanning detection tool for static analysis.

---

[简体中文](./README.md) | [English](./README_EN.md)

---

### # Jisuo

`Owl` is a static file feature detection tool provided by `TCA`, which can quickly find the source code file or dependency file that meets certain characteristics in the specified project directory. Why was this tool developed? For example, many times our project is too big, there are many dependent files in the project folder, such as a `Java` project introduces a `log4j` this` jar `dependency, there is a circular dependency problem in a file in the project. When there is a vulnerability in a dependency package, the tool can quickly scan the suspicious dependency files in the project directory, and give the address of the dependent files to help developers quickly locate the suspicious files.

### Reason

The current version of the function is relatively simple, the working principle is very simple, the tool will scan a specific directory through the built-in feature code algorithm to match a specific file, and then collect the file address that matches its feature code, and then show it, it can also be redirected to a fixed `json` file to save.

! [](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yvkgtmbwj20lo0ca0tl.jpg)

`Owl` is similar to anti-virus software, and the working principle of anti-virus software is similar, `Owl` will scan the entire project according to the signature code of the dependent file, and the anti-virus library works similarly. Of course, if it is done strictly in accordance with the standard of anti-virus software, it may involve some assembler related, the current `owl` function is not so complex, the later version will join the codeql code analysis engine, through the codeql database to do static analysis function enhancement.

### Start fast

How to use `owl`? You can clone the warehouse then by the following command:

```bash
git clone github.com:Tencent/CodeAnalysis.git
` ` `

Then switch the directory to `tools\owl` as follows:

```bash
cd CodeAnalysis/tools/owl
` ` `

There is a `Makefile` file inside the repository that can quickly help you build binaries for the corresponding platform, for example:

```bash
$: make help
make darwin	| Compile executable binary for MacOS platform
make linux	| Compile executable binary for Linux platform
make windows	| Compile executable binary for Windows platform
make clean	| Clean up executable binary
` ` `

** Note 📢 : ** If you do not have the `Go` environment configured on the machine, please configure the `Go` development environment before normal compilation, compilation cost binary you need to have `Go` cross-compilation knowledge, if there are problems welcome to `issued`.


### How to use

The completion of the program will get a binary file, the program name is` owl `, as follows` owl `execution effect, some subcommand parameters have been listed:

```bash
$: ./owl

_____  _    _  __
(_)(\/\/)()
)(_)()()(__
(_____)(__/\__)(____) 🦉 v0.1.3

A dependency module feature scanning detection tool for static analysis.


Usage:
owl [command]

Available Commands:
completion  Generate the autocompletion script for the specified shell
help        Help about any command
hex         File hex encoding
md5         Collection file md5
run         Execute the scanner
version     Version information

Flags:
-h, --help   help for owl

Use "owl [command] --help" for more information about a command.
` ` `

If you do not know how to use the subcommand, you can enter the `--help` parameter after the corresponding subcommand to get help information:

! [](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yz0laxdyj22ax0u07bb.jpg)

For example, if you want to find log4j, you first need to compute the log4j signature code through owl, as follows:

```bash
$:. / owl md5 -- -- path = / Users/ding/Downloads/log4j - 1.2.17. Jar
` ` `

** Note that the calculation of the feature code here must use the algorithm of the `owl` program, because the algorithm of the `owl` in the large file I use the fractional data block scheme to calculate, improve the running speed of the program, so if the use of other software algorithms then there will be problems! **

The results are as follows:

! [](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yz54cg72j22gm0e0af2.jpg)

You can also use the hexadecimal string feature to find:

```bash
$: / owl hex - path = / Users/ding/Downloads/log4j - 1.2.17. Jar
` ` `

The program will convert the corresponding file into a hexadecimal string display, as shown below:

! [](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yz7v68cbj217g0u0h0x.jpg)

Now you can use the scanner to scan, the matching mode can be specified as` md5 `or` hex `, more modes may be added in the future, the command is as follows:

```bash
$: ./owl run --dir=/Users/ding/Downloads/ --mode=md5 --code=04a41f0a068986f0f73485cf507c0f40
` ` `

Search for specific dependent files:

! [](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yze6emx3j21yq0dajwn.jpg)


** If there are too many search results, you can save the results through the `--out` parameter to save in a file, the file format is` json `! **

### Other

If you have any questions, you can raise `issue` on `TCA`, and if you have questions about this tool, you can add `owl` label on `issue` 🤝.
