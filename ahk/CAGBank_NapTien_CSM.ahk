SetTitleMatchMode, 2  ;

TaiKhoan := "tien"
SoTien := 2000

SetTitleMatchMode, 2  ;
WinActivate, Cyber Station Manager
Loop
{
    Send, {Esc}
    Sleep, 100  ; Đợi 100ms giữa mỗi lần bấm
    if WinActive("Cyber Station Manager")
        break  ; Thoát vòng lặp nếu cửa sổ đã active
}
BlockInput, On  ;
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
DllCall("ShowCursor", "Int", 1)  ;
BlockInput, Off  ;
ExitApp
