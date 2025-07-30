# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2025 Tencent
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
SCC 支持的语言类型及后缀名
"""


SCC_SUPPORTED_LANGUAGES = {
  "ABAP": [
    ".abap"
  ],
  "ActionScript": [
    ".as"
  ],
  "Ada": [
    ".ada",
    ".adb",
    ".ads",
    ".pad"
  ],
  "Agda": [
    ".agda"
  ],
  "Alchemist": [
    ".crn"
  ],
  "Alex": [
    ".x"
  ],
  "Alloy": [
    ".als"
  ],
  "Android Interface Definition Language": [
    ".aidl"
  ],
  "Arvo": [
    ".avdl",
    ".avpr",
    ".avsc"
  ],
  "AsciiDoc": [
    ".adoc"
  ],
  "ASP": [
    ".asa",
    ".asp"
  ],
  "ASP.NET": [
    ".asax",
    ".ascx",
    ".asmx",
    ".aspx",
    ".master",
    ".sitemap",
    ".webinfo"
  ],
  "Assembly": [
    ".s",
    ".asm"
  ],
  "ATS": [
    ".dats",
    ".sats",
    ".ats",
    ".hats"
  ],
  "Autoconf": [
    ".in"
  ],
  "AutoHotKey": [
    ".ahk"
  ],
  "AWK": [
    ".awk"
  ],
  "BASH": [
    ".bash",
    ".bash_login",
    ".bash_logout",
    ".bash_profile",
    ".bashrc",
    ".bash_login",
    ".bash_logout",
    ".bash_profile",
    ".bashrc"
  ],
  "Basic": [
    ".bas"
  ],
  "Batch": [
    ".bat",
    ".btm",
    ".cmd"
  ],
  "Bazel": [
    ".bzl",
    ".build.bazel",
    ".build",
    ".workspace"
  ],
  "Bitbake": [
    ".bb",
    ".bbappend",
    ".bbclass"
  ],
  "Bitbucket Pipeline": [
    ".bitbucket-pipelines.yml"
  ],
  "Boo": [
    ".boo"
  ],
  "Bosque": [
    ".bsq"
  ],
  "Brainfuck": [
    ".bf"
  ],
  "BuildStream": [
    ".bst"
  ],
  "C": [
    ".c",
    ".ec",
    ".pgc"
  ],
  "C Header": [
    ".h"
  ],
  "C Shell": [
    ".csh",
    ".cshrc"
  ],
  "C#": [
    ".cs"
  ],
  "C++": [
    ".cc",
    ".cpp",
    ".cxx",
    ".c++",
    ".pcc"
  ],
  "C++ Header": [
    ".hh",
    ".hpp",
    ".hxx",
    ".inl",
    ".ipp"
  ],
  "Cabal": [
    ".cabal"
  ],
  "Cargo Lock": [
    ".cargo.lock"
  ],
  "Cassius": [
    ".cassius"
  ],
  "Ceylon": [
    ".ceylon"
  ],
  "Clojure": [
    ".clj",
    ".cljc"
  ],
  "ClojureScript": [
    ".cljs"
  ],
  "Closure Template": [
    ".soy"
  ],
  "CMake": [
    ".cmake",
    ".cmakelists.txt"
  ],
  "COBOL": [
    ".cob",
    ".cbl",
    ".ccp",
    ".cobol",
    ".cpy"
  ],
  "CoffeeScript": [
    ".coffee"
  ],
  "Cogent": [
    ".cogent"
  ],
  "ColdFusion": [
    ".cfm"
  ],
  "ColdFusion CFScript": [
    ".cfc"
  ],
  "Coq": [
    ".v"
  ],
  "Creole": [
    ".creole"
  ],
  "Crystal": [
    ".cr"
  ],
  "CSS": [
    ".css"
  ],
  "CSV": [
    ".csv"
  ],
  "Cython": [
    ".pyx",
    ".pxi",
    ".pxd"
  ],
  "D": [
    ".d"
  ],
  "Dart": [
    ".dart"
  ],
  "Device Tree": [
    ".dts",
    ".dtsi"
  ],
  "Dhall": [
    ".dhall"
  ],
  "Docker ignore": [
    ".dockerignore"
  ],
  "Dockerfile": [
    ".dockerfile",
    ".dockerfile"
  ],
  "Document Type Definition": [
    ".dtd"
  ],
  "Elixir": [
    ".ex",
    ".exs"
  ],
  "Elm": [
    ".elm"
  ],
  "Emacs Dev Env": [
    ".ede"
  ],
  "Emacs Lisp": [
    ".el"
  ],
  "Erlang": [
    ".erl",
    ".hrl"
  ],
  "Expect": [
    ".exp"
  ],
  "Extensible Stylesheet Language Transformations": [
    ".xslt",
    ".xsl"
  ],
  "F#": [
    ".fs",
    ".fsi",
    ".fsx",
    ".fsscript"
  ],
  "F*": [
    ".fst"
  ],
  "FIDL": [
    ".fidl"
  ],
  "Fish": [
    ".fish"
  ],
  "Flow9": [
    ".flow"
  ],
  "Forth": [
    ".4th",
    ".forth",
    ".fr",
    ".frt",
    ".fth",
    ".f83",
    ".fb",
    ".fpm",
    ".e4",
    ".rx",
    ".ft"
  ],
  "FORTRAN Legacy": [
    ".f",
    ".for",
    ".ftn",
    ".f77",
    ".pfo"
  ],
  "FORTRAN Modern": [
    ".f03",
    ".f08",
    ".f90",
    ".f95"
  ],
  "Fragment Shader File": [
    ".fsh"
  ],
  "Freemarker Template": [
    ".ftl"
  ],
  "Futhark": [
    ".fut"
  ],
  "Game Maker Language": [
    ".gml"
  ],
  "Game Maker Project": [
    ".yyp"
  ],
  "GDScript": [
    ".gd"
  ],
  "Gemfile": [
    ".gemfile"
  ],
  "Gherkin Specification": [
    ".feature"
  ],
  "gitignore": [
    ".gitignore"
  ],
  "GLSL": [
    ".vert",
    ".tesc",
    ".tese",
    ".geom",
    ".frag",
    ".comp"
  ],
  "GN": [
    ".gn",
    ".gni"
  ],
  "Go": [
    ".go"
  ],
  "Go Template": [
    ".tmpl"
  ],
  "Gradle": [
    ".gradle"
  ],
  "Groovy": [
    ".groovy",
    ".grt",
    ".gtpl",
    ".gvy"
  ],
  "Hamlet": [
    ".hamlet"
  ],
  "Handlebars": [
    ".hbs",
    ".handlebars"
  ],
  "Happy": [
    ".y",
    ".ly"
  ],
  "Haskell": [
    ".hs"
  ],
  "Haxe": [
    ".hx"
  ],
  "HEX": [
    ".hex"
  ],
  "HTML": [
    ".html",
    ".htm"
  ],
  "IDL": [
    ".idl",
    ".webidl",
    ".widl"
  ],
  "Idris": [
    ".idr",
    ".lidr"
  ],
  "ignore": [
    ".ignore"
  ],
  "Intel HEX": [
    ".ihex"
  ],
  "Isabelle": [
    ".thy"
  ],
  "Jade": [
    ".jade"
  ],
  "JAI": [
    ".jai"
  ],
  "Janet": [
    ".janet"
  ],
  "Java": [
    ".java"
  ],
  "JavaScript": [
    ".js",
    ".mjs"
  ],
  "JavaServer Pages": [
    ".jsp"
  ],
  "Jenkins Buildfile": [
    ".jenkinsfile"
  ],
  "Jinja": [
    ".jinja",
    ".j2",
    ".jinja2"
  ],
  "JSON": [
    ".json"
  ],
  "JSONL": [
    ".jsonl"
  ],
  "JSX": [
    ".jsx"
  ],
  "Julia": [
    ".jl"
  ],
  "Julius": [
    ".julius"
  ],
  "Jupyter": [
    ".ipynb",
    ".jpynb"
  ],
  "Just": [
    ".justfile"
  ],
  "Korn Shell": [
    ".ksh",
    ".kshrc"
  ],
  "Kotlin": [
    ".kt",
    ".kts"
  ],
  "LaTeX": [
    ".tex"
  ],
  "LD Script": [
    ".lds"
  ],
  "Lean": [
    ".lean",
    ".hlean"
  ],
  "LESS": [
    ".less"
  ],
  "LEX": [
    ".l"
  ],
  "License": [
    ".license",
    ".licence",
    ".copying",
    ".copying3",
    ".unlicense",
    ".unlicence",
    ".license-mit",
    ".licence-mit",
    ".copyright"
  ],
  "Lisp": [
    ".lisp",
    ".lsp"
  ],
  "LOLCODE": [
    ".lol",
    ".lols"
  ],
  "Lua": [
    ".lua"
  ],
  "Lucius": [
    ".lucius"
  ],
  "Luna": [
    ".luna"
  ],
  "m4": [
    ".m4"
  ],
  "Macromedia eXtensible Markup Language": [
    ".mxml"
  ],
  "Madlang": [
    ".mad"
  ],
  "Makefile": [
    ".makefile",
    ".mak",
    ".mk",
    ".bp",
    ".makefile"
  ],
  "Mako": [
    ".mako",
    ".mao"
  ],
  "Markdown": [
    ".md",
    ".markdown"
  ],
  "Meson": [
    ".meson.build",
    ".meson_options.txt"
  ],
  "Modula3": [
    ".m3",
    ".mg",
    ".ig",
    ".i3"
  ],
  "Module-Definition": [
    ".def"
  ],
  "Monkey C": [
    ".mc"
  ],
  "MQL Header": [
    ".mqh"
  ],
  "MQL4": [
    ".mq4"
  ],
  "MQL5": [
    ".mq5"
  ],
  "MSBuild": [
    ".csproj",
    ".vbproj",
    ".fsproj",
    ".props",
    ".targets"
  ],
  "MUMPS": [
    ".mps"
  ],
  "Mustache": [
    ".mustache"
  ],
  "Nim": [
    ".nim"
  ],
  "Nix": [
    ".nix"
  ],
  "nuspec": [
    ".nuspec"
  ],
  "Objective C": [
    ".m"
  ],
  "Objective C++": [
    ".mm"
  ],
  "OCaml": [
    ".ml",
    ".mli"
  ],
  "Opalang": [
    ".opa"
  ],
  "Org": [
    ".org"
  ],
  "Oz": [
    ".oz"
  ],
  "Pascal": [
    ".pas"
  ],
  "Patch": [
    ".patch"
  ],
  "Perl": [
    ".pl",
    ".pm"
  ],
  "PHP": [
    ".php"
  ],
  "PKGBUILD": [
    ".pkgbuild"
  ],
  "PL/SQL": [
    ".fnc",
    ".pkb",
    ".pks",
    ".prc",
    ".trg",
    ".vw"
  ],
  "Plain Text": [
    ".text",
    ".txt"
  ],
  "Polly": [
    ".polly"
  ],
  "Pony": [
    ".pony"
  ],
  "Powershell": [
    ".ps1",
    ".psm1"
  ],
  "Processing": [
    ".pde"
  ],
  "Prolog": [
    ".p",
    ".pro"
  ],
  "Properties File": [
    ".properties"
  ],
  "Protocol Buffers": [
    ".proto"
  ],
  "PSL Assertion": [
    ".psl"
  ],
  "Puppet": [
    ".pp"
  ],
  "PureScript": [
    ".purs"
  ],
  "Python": [
    ".py"
  ],
  "Q#": [
    ".qs"
  ],
  "QCL": [
    ".qcl"
  ],
  "QML": [
    ".qml"
  ],
  "R": [
    ".r"
  ],
  "Rakefile": [
    ".rake",
    ".rakefile"
  ],
  "Razor": [
    ".cshtml"
  ],
  "Report Definition Language": [
    ".rdl"
  ],
  "ReStructuredText": [
    ".rst"
  ],
  "Robot Framework": [
    ".robot"
  ],
  "Ruby": [
    ".rb"
  ],
  "Ruby HTML": [
    ".rhtml"
  ],
  "Rust": [
    ".rs"
  ],
  "SAS": [
    ".sas"
  ],
  "Sass": [
    ".sass",
    ".scss"
  ],
  "Scala": [
    ".sc",
    ".scala"
  ],
  "Scheme": [
    ".scm",
    ".ss"
  ],
  "Scons": [
    ".csig",
    ".sconstruct",
    ".sconscript"
  ],
  "sed": [
    ".sed"
  ],
  "Shell": [
    ".sh",
    ".tcshrc"
  ],
  "Sieve": [
    ".sieve"
  ],
  "SKILL": [
    ".il"
  ],
  "Smarty Template": [
    ".tpl"
  ],
  "Softbridge Basic": [
    ".sbl"
  ],
  "SPDX": [
    ".spdx"
  ],
  "Specman e": [
    ".e"
  ],
  "Spice Netlist": [
    ".ckt"
  ],
  "SQL": [
    ".sql"
  ],
  "SRecode Template": [
    ".srt"
  ],
  "Standard ML (SML)": [
    ".sml"
  ],
  "Stata": [
    ".do",
    ".ado"
  ],
  "Stylus": [
    ".styl"
  ],
  "SVG": [
    ".svg"
  ],
  "Swift": [
    ".swift"
  ],
  "Swig": [
    ".i"
  ],
  "Systemd": [
    ".automount",
    ".device",
    ".link",
    ".mount",
    ".path",
    ".scope",
    ".service",
    ".slice",
    ".socket",
    ".swap",
    ".target",
    ".timer"
  ],
  "SystemVerilog": [
    ".sv",
    ".svh"
  ],
  "TaskPaper": [
    ".taskpaper"
  ],
  "TCL": [
    ".tcl"
  ],
  "Terraform": [
    ".tf",
    ".tf.json"
  ],
  "TeX": [
    ".tex",
    ".sty"
  ],
  "Thrift": [
    ".thrift"
  ],
  "TOML": [
    ".toml"
  ],
  "Twig Template": [
    ".twig"
  ],
  "TypeScript": [
    ".ts",
    ".tsx"
  ],
  "TypeScript Typings": [
    ".d.ts"
  ],
  "Unreal Script": [
    ".uc",
    ".uci",
    ".upkg"
  ],
  "Ur/Web": [
    ".ur",
    ".urs"
  ],
  "Ur/Web Project": [
    ".urp"
  ],
  "V": [
    ".v"
  ],
  "Vala": [
    ".vala"
  ],
  "Varnish Configuration": [
    ".vcl"
  ],
  "Verilog": [
    ".vg",
    ".vh",
    ".v"
  ],
  "Verilog Args File": [
    ".irunargs",
    ".xrunargs"
  ],
  "Vertex Shader File": [
    ".vsh"
  ],
  "VHDL": [
    ".vhd",
    ".vhdl"
  ],
  "Vim Script": [
    ".vim"
  ],
  "Visual Basic": [
    ".vb"
  ],
  "Visual Basic for Applications": [
    ".cls"
  ],
  "Vue": [
    ".vue"
  ],
  "Web Services Description Language": [
    ".wsdl"
  ],
  "Wolfram": [
    ".nb",
    ".wl"
  ],
  "Wren": [
    ".wren"
  ],
  "XAML": [
    ".xaml"
  ],
  "Xcode Config": [
    ".xcconfig"
  ],
  "XML": [
    ".xml"
  ],
  "XML Schema": [
    ".xsd"
  ],
  "Xtend": [
    ".xtend"
  ],
  "YAML": [
    ".yaml",
    ".yml"
  ],
  "Yarn": [
    ".yarn"
  ],
  "Zig": [
    ".zig"
  ],
  "Zsh": [
    ".zsh",
    ".zshenv",
    ".zlogin",
    ".zlogout",
    ".zprofile",
    ".zshrc",
    ".zshenv",
    ".zlogin",
    ".zlogout",
    ".zprofile",
    ".zshrc"
  ]
}
