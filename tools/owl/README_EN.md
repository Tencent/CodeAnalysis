# Owl🦉

A dependency module feature scanning detection tool for static analysis.

---

[简体中文](./README.md) | [English](./README_EN.md)

---

### Introduction

`Owl` is a static file feature detection tool provided by `TCA`, which can quickly find the source code file or dependency files that meet certain characteristics in the specified project directory. Why was this tool developed? For example, many times our projects are large, and there are many dependency files in the project folder. For instance, in a Java project, let’s say we have imported the `log4j` jar dependency, and there is a circular dependency issue in one of the project files. When a vulnerability is found in a particular dependency package, this tool can quickly scan the suspicious dependency files in the project directory and provide the location of the dependency file, helping developers to quickly locate the suspicious file.

### Principle

The current version of the tool has relatively simple functionality, and the working principle is straightforward. The tool scans a specific directory and matches specific files through a built-in feature code algorithm. It then collects the file addresses that match their feature codes and displays them or redirects them to a fixed `JSON` file for storage.

![](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yvkgtmbwj20lo0ca0tl.jpg)

`Owl` is similar to a antivirus software, it works on the principle of a antivirus software. `Owl` scans the entire project based on the feature codes of the dependency files, similar to the working principle of an antivirus virus library. Of course, if it strictly follows the standards of antivirus software, it may involve some assembly-related components. Currently, the functionality of `owl` is not that complex, but future versions will include the `codeql` code analysis engine to enhance the static analysis functionality using `CodeQL`'s database.

### Quick Start

How to use `owl`? You can clone the repository and then use the following command:

```bash
git clone github.com:Tencent/CodeAnalysis.git
```

Then navigate to the `tools\owl` directory, like this:

```bash
cd CodeAnalysis/tools/owl
```

Inside the repository, there is a `Makefile` that can help you quickly build the binary file for the corresponding platform, for example:

```bash
$: make help
make darwin	| Compile executable binary for MacOS platform
make linux	| Compile executable binary for Linux platform
make windows	| Compile executable binary for Windows platform
make clean	| Clean up executable binary
```

**Note 📢:**  If you do not have the `Go` environment configured on the machine, please configure the `Go` development environment before executing the compilation. To compile into a local binary file, you need to have the knowledge of `Go` cross-compilation. If there are problems welcome to `issues`.

### How to use

After building the program, you will get a binary file named ` owl `. The following shows the execution result of ` owl `, with some subcommand parameters listed:

```bash
$: ./owl

			 _____  _    _  __
			(  _  )( \/\/ )(  )
			 )(_)(  )    (  )(__
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
```

If you do not know how to use the subcommand, you can enter the `--help` parameter after the corresponding subcommand to get help information:

![](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yz0laxdyj22ax0u07bb.jpg)

For example, if you want to search for `log4j`, firstly you need to calculate the feature code of `log4j` using `owl`. The command is as follows:

```bash
$: ./owl md5 --path=/Users/ding/Downloads/log4j-1.2.17.jar
```

**Note that the feature code calculation here must use the algorithm provided by the `owl` program. The algorithm in `owl` is designed for handling large files using a data block-based approach to improve program execution speed. So if you use algorithms from other software, there may be issues!**

The results are as follows:

![](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yz54cg72j22gm0e0af2.jpg)

You can also use the hexadecimal string feature for searching:

```bash
$: ./owl hex --path=/Users/ding/Downloads/log4j-1.2.17.jar
```

The program will convert the corresponding file into a hexadecimal string for display, as shown in the following image:

![](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yz7v68cbj217g0u0h0x.jpg)

Now you can use the scanner to scan, the matching mode can be specified as` md5 `or` hex `, more modes may be added in the future, the command is as follows:

```bash
$: ./owl run --dir=/Users/ding/Downloads/ --mode=md5 --code=04a41f0a068986f0f73485cf507c0f40
```

Search for specific dependent files:

![](https://tva1.sinaimg.cn/large/e6c9d24egy1h2yze6emx3j21yq0dajwn.jpg)


**If there are too many search results, you can save the results through the `--out` parameter to save in a file, whose format is` json `!**

### Others

If you have any questions, you can raise `issue` on `TCA`, and if you have questions about this tool, you can add `owl` tag on the `issue` 🤝.
