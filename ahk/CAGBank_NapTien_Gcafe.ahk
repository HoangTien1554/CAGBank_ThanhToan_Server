SetTitleMatchMode, 2  ;

TaiKhoan := "nhat11"
SoTien := 5000
BlockInput, On  ;
WinActivate, GCafe+ server 1.7.45 [ADMIN (Điều hành)] ;
WinWaitActive, GCafe+ server 1.7.45 [ADMIN (Điều hành)] ;
CoordMode, Mouse, Screen  ;
Sleep, 150 ;
Click, 131, 100 ;
Sleep, 150 ;
Click, 368, 135 ;
Sleep, 50 ;
Send, ^a
Sleep, 50 ;
Send, %TaiKhoan% ;
Sleep, 150 ;
SendInput, {Enter} ;
Sleep, 150 ;
Click, 58, 188 ;
Sleep, 150 ;
Click, 58, 188 ;
Sleep, 150 ;
Click, 1310, 510 ;
Sleep, 150 ;
Send, %SoTien% ;
Sleep, 150 ;
Click, 913, 617 ;
Sleep, 150 ;
Click, 914, 767 ;
Sleep, 150 ;
BlockInput, Off  ;
ExitApp
