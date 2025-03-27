SetTitleMatchMode, 2  ;

TaiKhoan := "tien"
SoTien := 10000
BlockInput, On  ;
WinActivate, Cyber Station Manager - [ Nhan vien: ADMIN (Admin) ] ;
WinWaitActive, Cyber Station Manager - [ Nhan vien: ADMIN (Admin) ] ;
CoordMode, Mouse, Screen  ;
Sleep, 100 ;
Click, 140, 100 ;
Sleep, 100 ;
Click, 440, 176 ;
Sleep, 50 ;
Send, ^a
Sleep, 50 ;
Send, %TaiKhoan% ;
Sleep, 100 ;
SendInput, {Enter} ;
Sleep, 100 ;
Click, 100, 235 ;
Sleep, 100 ;
Click, 100, 235 ;
Sleep, 100 ;
Click, 1295, 540 ;
Sleep, 100 ;
Send, %SoTien% ;
Sleep, 100 ;
Click, 920, 630 ;
Sleep, 100 ;
Click, 960, 560 ;
Sleep, 100 ;
Click, 910, 730 ;
Sleep, 100 ;
BlockInput, Off  ;
ExitApp
