@echo off
@title =  Auto Installer for Faith Tools
SET CopyDirDestination=%UserProfile%\Documents\maya
SET CopyDirSource=%~dp0
SET CopyDirSourceGlobal=%UserProfile%\Documents\maya\scripts
SET CopyDirSourceMel=%~dp0mel-scripts
SET CopyDirSourcePy=%~dp0python-scripts
SET ImportCommandSearch=source\ \"tool_menu.mel\";
SET ExtractionDirPython=%~dp0python-scripts
SET ExtractionDirMel=%~dp0mel-scripts

:MENU
@echo off
cls
color 0A
@echo on
@echo.
@echo.
@echo -----------------------------------------------------------------------
@echo ----//---/-/------------------------------/__--___/--------------------
@echo ---//___---___-----(-)-__--___-/-__---------/-/---___------___-----//--
@echo --/-___--//---)-)-/-/---/-/---//---)-)-----/-/--//---)-)-//---)-)-//---
@echo -//-----//---/-/-/-/---/-/---//---/-/-----/-/--//---/-/-//---/-/-//----
@echo //-----((___(-(-/-/---/-/---//---/-/-----/-/--((___/-/-((___/-/-//-----
@echo.
@echo.
@echo.
@echo. 	1 = Install Faith Tools
@echo. 	2 = Uninstall Faith Tools
@echo. 	3 = About Installer
@echo.
@echo.
@echo off
SET /P M=Type 1, 2 or 3 then press ENTER:
IF %M%==1 GOTO INSTALL
IF %M%==2 GOTO UNINSTALL
IF %M%==3 GOTO ABOUT
GOTO EOF

REM Main Function
:INSTALL

IF NOT EXIST %ExtractionDirPython% ( GOTO SETUP_MISSING_SCRIPTS ) 
IF NOT EXIST %ExtractionDirMel% ( GOTO SETUP_MISSING_SCRIPTS ) 
IF EXIST %CopyDirDestination% (
	GOTO valid_maya_dir
) ELSE (
	GOTO missing_maya_dir
)

:valid_maya_dir
CD /D %CopyDirDestination%
for /D %%s in (.\*) do CALL :get_maya_folders %%s
CALL :valid_maya_dir_global
IF %RobocopyError%==1 GOTO robocopy_error
GOTO INSTALLATION_COMPLETE
EXIT /B %ERRORLEVEL% 

REM Start installation for every version
:get_maya_folders
echo %~1|findstr /r "[0-9][0-9][0-9][0-9]" >nul  && ( CALL :build_path %%~1 )
EXIT /B 0

:build_path
SET version=%~1
SET version_no_dot=%version:.=%
CALL :copy_files %CopyDirDestination%%version_no_dot%\scripts
CALL :check_usersetup_existence %CopyDirDestination%%version_no_dot%\scripts
EXIT /B 0

:copy_files
SET RobocopyError=0
ROBOCOPY "%CopyDirSource% " "%~1 " /Z /IF "*.py" /njh /njs /ndl /nc /ns
IF %ERRORLEVEL%==16 SET RobocopyError=1
ROBOCOPY "%CopyDirSource% " "%~1 "  /Z /IF "*.mel" /njh /njs /ndl /nc /ns
IF %ERRORLEVEL%==16 SET RobocopyError=1
IF EXIST "%CopyDirSourceMel% " (
	ROBOCOPY "%CopyDirSourceMel% " "%~1 "  /Z /IF "*.mel" /XF "userSetup*" /njh /njs /ndl /nc /ns
	IF %ERRORLEVEL%==16 SET RobocopyError=1
) 
IF EXIST "%CopyDirSourcePy% " (
	ROBOCOPY "%CopyDirSourcePy%" "%~1 " /e
	IF %ERRORLEVEL%==16 SET RobocopyError=1
) 
EXIT /B 0

:check_usersetup_existence
SET UserSetupPath=%~1\userSetup.mel
IF EXIST %UserSetupPath% ( CALL :check_import_existence %UserSetupPath% ) ELSE ( CALL :create_new_usersetup %UserSetupPath% )
EXIT /B 0

:check_import_existence
>nul findstr "%ImportCommandSearch%" %~1 && (
  REM import already present
) || (
  CALL :add_import %~1
)
EXIT /B 0

:add_import
ECHO. >> %~1
echo %ImportCommand% >> %~1
EXIT /B 0

:create_new_usersetup
echo %ImportCommand% >> %~1
EXIT /B 0


REM Global userSetup Check
:valid_maya_dir_global
IF EXIST %CopyDirSourceGlobal% ( CALL :check_usersetup_existence_global ) 
EXIT /B 0

:check_usersetup_existence_global
SET GlobalUsersetupPath=%CopyDirSourceGlobal%\userSetup.mel
IF EXIST %GlobalUsersetupPath% ( CALL :global_usersetup_exists %GlobalUsersetupPath% ) 
EXIT /B 0

:global_usersetup_exists
>nul findstr "%ImportCommandSearch%" %~1 && (
  REM import already present
) || (
  CALL :add_import_global_usersetup %~1
)
EXIT /B 0

:add_import_global_usersetup
ECHO. >> %~1
echo %ImportCommand% >> %~1
EXIT /B 0


REM Start uninstall
:UNINSTALL
tasklist /FI "IMAGENAME eq maya.exe" | findstr "maya.exe" >nul
IF %ERRORLEVEL% == 1 GOTO APP_NOT_RUNNING_UNINSTALL
GOTO APP_RUNNING_UNINSTALL

:APP_NOT_RUNNING_UNINSTALL
IF EXIST %CopyDirDestination% (
	GOTO VALID_MAYA_DIR_UNINSTALL
) ELSE (
	GOTO MISSING_MAYA_DIR_UNINSTALL
)

:VALID_MAYA_DIR_UNINSTALL
CD /D %CopyDirDestination%
for /D %%s in (.\*) do CALL :get_maya_folders_uninstall %%s
CALL :check_usersetup_existence_global_uninstall
GOTO UNINSTALLATION_COMPLETE
EXIT /B %ERRORLEVEL% 

:get_maya_folders_uninstall
echo %~1|findstr /r "[0-9][0-9][0-9][0-9]" >nul  && ( CALL :build_path_uninstall %%~1 )
EXIT /B 0

:build_path_uninstall
SET version=%~1
SET version_no_dot=%version:.=%
CALL :remove_files %CopyDirDestination%%version_no_dot%\scripts
CALL :check_usersetup_existence_uninstall %CopyDirDestination%%version_no_dot%\scripts
EXIT /B 0

:check_usersetup_existence_global_uninstall
SET GlobalUsersetupPath=%CopyDirSourceGlobal%\userSetup.mel
IF EXIST %GlobalUsersetupPath% ( CALL :global_usersetup_exists_uninstall %GlobalUsersetupPath% ) 
EXIT /B 0

:global_usersetup_exists_uninstall
>nul findstr "%ImportCommandSearch%" %~1 && ( CALL :remove_import %~1 ) 
EXIT /B 0

:check_usersetup_existence_uninstall
SET UserSetupPath=%~1\userSetup.mel
IF EXIST %UserSetupPath% ( CALL :check_import_existence_uninstall %UserSetupPath% )
EXIT /B 0

:check_import_existence_uninstall
>nul findstr "%ImportCommandSearch%" %~1 && ( CALL :remove_import %~1 ) 
EXIT /B 0

:remove_import
SET "TEMP_USERSETUP=%TEMP%\%RANDOM%__hosts"
findstr /V "%ImportCommandSearch%" "%~1" > "%TEMP_USERSETUP%"
COPY /b/v/y "%TEMP_USERSETUP%" "%~1"
(for /f usebackq^ eol^= %%a in (%~1) do break) && echo userSetup has data || del %~1
EXIT /B 0

REM Install Feedback
:missing_maya_dir
@echo off
color 0C
cls
@echo on
@echo.
@echo.
@echo       ллллллл лллллл  лллллл   лллллл  лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллл   лллллл  лллллл  лл    лл лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллллл лл   лл лл   лл  лллллл  лл   лл 
@echo.
@echo.
@echo       Maya directory was not found. 
@echo       You might have to install the scripts manually.
@echo       Learn how to fix this issue in the "About Installer" option.
@echo.
@echo.
@echo off
SET /P AREYOUSURE=Would you like to open the instructions for the manual installation (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO EOF
start "" %ManualInstallationURL%
GOTO EOF

:robocopy_error
@echo off
color 0C
cls
@echo on
@echo.
@echo.
@echo       ллллллл лллллл  лллллл   лллллл  лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллл   лллллл  лллллл  лл    лл лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллллл лл   лл лл   лл  лллллл  лл   лл 
@echo.
@echo.
@echo       An error was raised when copying the files. 
@echo       The installation might have succeeded, but the script can't confirm that. 
@echo       You might have to install the scripts manually.
@echo       Learn how to possibly fix this issue in the "About Installer" option.
@echo.
@echo.
@echo off
SET /P AREYOUSURE=Would you like to open the instructions for the manual installation (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO EOF
start "" %ManualInstallationURL%
GOTO EOF

:INSTALLATION_COMPLETE
@echo off
color 0A
cls
@echo on
@echo.   
@echo.                                   
@echo       лллллл   лллллл  ллл    лл ллллллл 
@echo       лл   лл лл    лл лллл   лл лл      
@echo       лл   лл лл    лл лл лл  лл ллллл   
@echo       лл   лл лл    лл лл  лл лл лл      
@echo       лллллл   лллллл  лл   лллл ллллллл 
@echo.     
@echo.  
@echo       Please restart Maya to load scripts.
@echo.  
@echo. 
@echo off      
pause               
GOTO EOF

REM Uninstall Feedback
:MISSING_MAYA_DIR_UNINSTALL
@echo off
color 0C
cls
@echo on
@echo.
@echo.
@echo       ллллллл лллллл  лллллл   лллллл  лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллл   лллллл  лллллл  лл    лл лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллллл лл   лл лл   лл  лллллл  лл   лл 
@echo.
@echo.
@echo       Maya directory was not found. 
@echo       You might have to uninstall the scripts manually.
@echo       Learn how to fix this issue in the "About Installer" option.
@echo.
@echo.
@echo off
SET /P AREYOUSURE=Would you like to open the instructions for the manual uninstallation (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO EOF
start "" %ManualInstallationURL%
GOTO EOF


:APP_RUNNING_UNINSTALL
@echo off
color 0C
cls
@echo on
@echo.
@echo.
@echo       ллллллл лллллл  лллллл   лллллл  лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллл   лллллл  лллллл  лл    лл лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллллл лл   лл лл   лл  лллллл  лл   лл 
@echo.
@echo.
@echo       Process named "maya.exe" was found.
@echo       Please close Maya before uninstalling.
@echo.
@echo.
@echo off
pause
GOTO MENU


:UNINSTALLATION_COMPLETE
@echo off
color 0A
cls
@echo on
@echo.   
@echo.                                   
@echo       лллллл   лллллл  ллл    лл ллллллл 
@echo       лл   лл лл    лл лллл   лл лл      
@echo       лл   лл лл    лл лл лл  лл ллллл   
@echo       лл   лл лл    лл лл  лл лл лл      
@echo       лллллл   лллллл  лл   лллл ллллллл 
@echo.     
@echo.  
@echo       Scripts were removed.
@echo       Import line was erased from userSetup.mel
@echo.  
@echo. 
@echo off      
pause                   
GOTO EOF


:SETUP_MISSING_SCRIPTS
@echo off
color 0C
cls
@echo on
@echo.
@echo.
@echo       ллллллл лллллл  лллллл   лллллл  лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллл   лллллл  лллллл  лл    лл лллллл  
@echo       лл      лл   лл лл   лл лл    лл лл   лл 
@echo       ллллллл лл   лл лл   лл  лллллл  лл   лл 
@echo.
@echo.
@echo       The setup file can't find the scripts.
@echo       Missing "mel-scripts" or "python-scripts".
@echo       Did you properly extract the files before running it?
@echo.
@echo.
@echo off
pause
GOTO MENU


:ABOUT
@echo off
color 02
cls
@echo on
@echo.
@echo.                _
@echo.               ( )                 GT Tools Setup
@echo.                H                  
@echo.                H                  This batch file attempts to automatically install all python and mel
@echo.               _H_                 scripts for GT Tools so the user doesn't need to mannualy copy them.
@echo.            .-'-.-'-.
@echo.           /         \             It assumes that Maya preferences are stored in the default path
@echo.          !           !            under "Documents\maya\####"  (#### being the version number)
@echo.          !   .-------'._          
@echo.          !  / /  '.' '. \         This is what the script does when installing:
@echo.          !  \ \ @   @ / /         1. It copies necessary scripts to all "maya\####\scripts" folders.
@echo.          !   '---------'          2. It looks for the "userSetup.mel" file to add the initialization line.
@echo.          !    _______!            (This process will not affect existing lines inside your "userSetup.mel")
@echo.          !  .'-+-+-+!             3. If "userSetup.mel" is not found, one will be created.
@echo.          !  '.-+-+-+!             
@echo.          !    """""" !            This is what the script does when uninstalling:
@echo.          '-._______.-'            1. It removes the installed scripts.
@echo.                                   2. It removes the initialization lines from all "userSetup.mel" files.
@echo. 
@echo. 
@echo. 
@echo off
pause
GOTO MENU

:EOF
EXIT