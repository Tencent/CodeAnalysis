#!/bin/bash

PWD=$(cd "$(dirname "$0")"; pwd)
TOOLS_DIR="$PWD/../../tools"
# echo $TOOLS_DIR
OS=`uname -s`

# install cppcheck
# CPPCHECK_HOME="$TOOLS_DIR/cppcheck-1.78"
# wget https://codeload.github.com/danmar/cppcheck/zip/1.78 -O $CPPCHECK_HOME.zip
# unzip $CPPCHECK_HOME.zip -d $TOOLS_DIR
# cd $CPPCHECK_HOME
# make install
# cd $PWD

# install pylint
pip3 install -q pylint==2.6.0

# install semgrep
pip3 install -q semgrep==0.100.0
# SEMGREP_HOME="$TOOLS_DIR/semgrep"
# SEMGREP_RULES_HOME="$SEMGREP_HOME/rules"
# cd $SEMGREP_HOME
# git clone https://github.com/returntocorp/semgrep-rules.git
# cp -r $SEMGREP_HOME/semgrep-rules/java/log4j $SEMGREP_RULES_HOME
# cd "$SEMGREP_HOME/semgrep-rules"
# git checkout e5f4517b1d2c6d63172ed013598a553e416f2428
# cp -r $SEMGREP_HOME/semgrep-rules/{c,generic,go,html,java,javascript,php,python,ruby,typescript,yaml} $SEMGREP_RULES_HOME
# rm -rf "$SEMGREP_HOME/semgrep-rules"

# # install Flawfinder
# FLAWFINDER_HOME="$TOOLS_DIR/flawfinder"
# wget https://github.com/david-a-wheeler/flawfinder/archive/refs/tags/2.0.18.zip -O $PWD/flawfinder.zip
# unzip $PWD/flawfinder.zip -d $PWD/
# cp -r $PWD/flawfinder-2.0.18 $FLAWFINDER_HOME/tool
# rm -rf $PWD/flawfinder-2.0.18/ $PWD/flawfinder.zip

# # install SpotBugs
# SPOTBUGS_HOME="$TOOLS_DIR/spotbugs-4.2.1"
# wget https://github.com/spotbugs/spotbugs/releases/download/4.2.1/spotbugs-4.2.1.zip -O $SPOTBUGS_HOME.zip
# unzip $SPOTBUGS_HOME.zip -d $TOOLS_DIR

# # install ShellCheck
# SHELLCHECK_HOME="$TOOLS_DIR/shellcheck"
# if [ ${OS} == "Darwin"  ];then
#     wget https://github.com/koalaman/shellcheck/releases/download/v0.7.1/shellcheck-v0.7.1.darwin.x86_64.tar.xz -O $PWD/shellcheck.tar.xz
#     tar -xvJf $PWD/shellcheck.tar.xz -C $PWD/
#     cp $PWD/shellcheck-v0.7.1/shellcheck $SHELLCHECK_HOME/shellcheck_mac
# elif [ ${OS} == "Linux"  ];then
#     wget https://github.com/koalaman/shellcheck/releases/download/v0.7.1/shellcheck-v0.7.1.linux.x86_64.tar.xz -O $PWD/shellcheck.tar.xz
#     tar -xvJf $PWD/shellcheck.tar.xz -C $PWD/
#     cp $PWD/shellcheck-v0.7.1/shellcheck $SHELLCHECK_HOME/shellcheck
# else
#     echo "Other OS: ${OS}"
# fi
# rm -rf $PWD/shellcheck-v0.7.1

# # install CheckStyle
# CHECKSTYLE_HOME="$TOOLS_DIR/checkstyle-8.29"
# wget https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.29/checkstyle-8.29-all.jar -O $CHECKSTYLE_HOME/checkstyle.jar

# # install Findbugs
# FINDBUGS_HOME="$TOOLS_DIR/findbugs-3.0.1"
# wget --no-check-certificate https://nchc.dl.sourceforge.net/project/findbugs/findbugs/3.0.1/findbugs-3.0.1.zip -O $FINDBUGS_HOME.zip
# unzip $FINDBUGS_HOME.zip -d $TOOLS_DIR
# rm $FINDBUGS_HOME.zip

# # install GolangciLint
# GCILINT_HOME="$TOOLS_DIR/golangci-lint-1.21.0"
# if [ ${OS} == "Darwin"  ];then
#     wget https://github.com/golangci/golangci-lint/releases/download/v1.21.0/golangci-lint-1.21.0-darwin-amd64.tar.gz -O $PWD/golangci-lint-1.21.0-darwin-amd64.tar.gz
#     tar -zxvf $PWD/golangci-lint-1.21.0-darwin-amd64.tar.gz -C $PWD/
#     cp $PWD/golangci-lint-1.21.0-darwin-amd64/golangci-lint $GCILINT_HOME/golangci-lint
# elif [ ${OS} == "Linux"  ];then
#     wget https://github.com/golangci/golangci-lint/releases/download/v1.21.0/golangci-lint-1.21.0-linux-amd64.tar.gz  -O $PWD/golangci-lint-1.21.0-linux-amd64.tar.gz
#     tar -zxvf $PWD/golangci-lint-1.21.0-linux-amd64.tar.gz -C $PWD/
#     cp $PWD/golangci-lint-1.21.0-darwin-amd64/golangci-lint $GCILINT_HOME/golangci-lint
# else
#     echo "Other OS: ${OS}"
# fi
# rm -rf $PWD/golangci-lint-1.21.0-darwin-amd64/

# # install Cloc
# CLOC_HOME="$TOOLS_DIR/cloc-1.84"
# wget https://github.com/AlDanial/cloc/releases/download/1.84/cloc-1.84.tar.gz -O $PWD/cloc-1.84.tar.gz
# tar -zxvf $PWD/cloc-1.84.tar.gz -C $PWD/
# mv $PWD/cloc-1.84 $CLOC_HOME
