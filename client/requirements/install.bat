@ECHO OFF

SETLOCAL

CD %~dp0
SET PWD=%CD%
SET TOOLS_DIR="%PWD%\..\..\tools"
SET "dnld=bitsadmin /transfer myDownloadJob /download /priority normal"

@REM ECHO install cppcheck
@REM SET CPPCHECK_HOME="%TOOLS_DIR%/cppcheck-1.78"
@REM %dnld% https://codeload.github.com/danmar/cppcheck/zip/1.78 %CPPCHECK_HOME%.zip
@REM CALL :UnZipFile %TOOLS_DIR% %CPPCHECK_HOME%.zip
@REM cd $CPPCHECK_HOME
@REM msbuild cppcheck.sln
@REM cd $PWD

ECHO install pylint
pip3 install pylint==2.6.0

ECHO install semgrep
pip3 install semgrep==0.100.0
@REM SET SEMGREP_HOME="%TOOLS_DIR%/semgrep"
@REM SET SEMGREP_RULES_HOME="%SEMGREP_HOME%/rules"
@REM cd %SEMGREP_HOME%
@REM git clone https://github.com/returntocorp/semgrep-rules.git
@REM XCOPY /s %SEMGREP_HOME%/semgrep-rules/java/log4j %SEMGREP_RULES_HOME%
@REM cd "%SEMGREP_HOME%/semgrep-rules"
@REM git checkout e5f4517b1d2c6d63172ed013598a553e416f2428
@REM XCOPY /s %SEMGREP_HOME%/semgrep-rules/{c,generic,go,html,java,javascript,php,python,ruby,typescript,yaml} %SEMGREP_RULES_HOME%
@REM RMDIR /s/q "%SEMGREP_HOME%/semgrep-rules"

@REM ECHO install Flawfinder
@REM SET FLAWFINDER_HOME="%TOOLS_DIR%/flawfinder"
@REM %dnld% https://github.com/david-a-wheeler/flawfinder/archive/refs/tags/2.0.18.zip %PWD%/flawfinder.zip
@REM CALL :UnZipFile %PWD% %PWD%/flawfinder.zip
@REM XCOPY /s %PWD%/flawfinder-2.0.18 %FLAWFINDER_HOME%/tool
@REM RMDIR /s/q %PWD%/flawfinder-2.0.18/ %PWD%/flawfinder.zip

@REM ECHO install SpotBugs
@REM SET SPOTBUGS_HOME="%TOOLS_DIR%/spotbugs-4.2.1"
@REM %dnld% https://github.com/spotbugs/spotbugs/releases/download/4.2.1/spotbugs-4.2.1.zip %SPOTBUGS_HOME%.zip
@REM CALL :UnZipFile %TOOLS_DIR% %SPOTBUGS_HOME%.zip

@REM ECHO install ShellCheck
@REM SET SHELLCHECK_HOME="%TOOLS_DIR%\shellcheck"
@REM %dnld% https://github.com/koalaman/shellcheck/releases/download/stable/shellcheck-stable.zip %PWD%\shellcheck-stable.zip
@REM if exist %PWD%\shellcheck RMDIR /s/q %PWD%\shellcheck
@REM CALL :UnZipFile %PWD%\shellcheck %PWD%\shellcheck-stable.zip
@REM XCOPY /s %PWD%\shellcheck\shellcheck.exe %SHELLCHECK_HOME%\shellcheck\shellcheck-stable.exe
@REM RMDIR /s/q %PWD%\shellcheck

@REM ECHO install CheckStyle
@REM CHECKSTYLE_HOME="%TOOLS_DIR%\checkstyle-8.29"
@REM %dnld% https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.29/checkstyle-8.29-all.jar %CHECKSTYLE_HOME%\checkstyle.jar

@REM ECHO install Findbugs
@REM FINDBUGS_HOME="%TOOLS_DIR%\findbugs-3.0.1"
@REM %dnld% https://nchc.dl.sourceforge.net/project/findbugs/findbugs/3.0.1/findbugs-3.0.1.zip %FINDBUGS_HOME%.zip
@REM CALL :UnZipFile %FINDBUGS_HOME%.zip %FINDBUGS_HOME%

@REM ECHO install GolangciLint
@REM @REM https://github.com/golangci/golangci-lint/releases/download/v1.21.0/golangci-lint-1.21.0-windows-amd64.zip

@REM ECHO install Cloc
@REM CLOC_HOME="%TOOLS_DIR%\cloc-1.84"
@REM %dnld% https://github.com/AlDanial/cloc/releases/download/1.84/cloc-1.84.exe %CLOC_HOME%\cloc-1.84.exe
@REM XCOPY /s %CLOC_HOME%\cloc-1.84.exe %CLOC_HOME%\cloc.exe

@REM ENDLOCAL

@REM PAUSE
@REM EXIT /B 0

@REM :UnZipFile <ExtractTo> <newzipfile>
@REM set vbs="%PWD%\_.vbs"
@REM if exist %vbs% del /f /q %vbs%
@REM >%vbs%  echo Set fso = CreateObject("Scripting.FileSystemObject")
@REM >>%vbs% echo If NOT fso.FolderExists("%1") Then
@REM >>%vbs% echo fso.CreateFolder("%1")
@REM >>%vbs% echo End If
@REM >>%vbs% echo set objShell = CreateObject("Shell.Application")
@REM >>%vbs% echo set FilesInZip=objShell.NameSpace("%2").items
@REM >>%vbs% echo objShell.NameSpace("%1").CopyHere(FilesInZip)
@REM >>%vbs% echo Set fso = Nothing
@REM >>%vbs% echo Set objShell = Nothing
@REM cscript //nologo %vbs%
@REM if exist %vbs% del /f /q %vbs%
