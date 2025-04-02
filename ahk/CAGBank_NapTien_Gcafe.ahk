SetTitleMatchMode, 2  ;

TaiKhoan := "nam001"
SoTien := 3348

BlockInput, On  ;
SetTitleMatchMode, 2  ; Cho phép tìm kiếm tiêu đề chứa chuỗi con
WinActivate, GCafe+ server 1.7.45
Loop
{
    Send, {Esc}
    Sleep, 100  ; Đợi 100ms giữa mỗi lần bấm
    if WinActive("GCafe+ server 1.7.45")
        break  ; Thoát vòng lặp nếu cửa sổ đã active
}
CoordMode, Mouse, Screen  ;
Sleep, 100 ;
Click, 131, 100 ;
Sleep, 100 ;
Click, 368, 135 ;
Sleep, 50 ;
Send, ^a
Sleep, 50 ;
Send, %TaiKhoan% ;
Sleep, 50 ;
SendInput, {Enter} ;
Sleep, 100 ;
Click, 58, 188 ;
Sleep, 100 ;
Click, 58, 188 ;
Sleep, 100 ;
Click, 1310, 510 ;
Sleep, 100 ;
Send, %SoTien% ;
Sleep, 50 ;
SendInput, {Enter} ;
Sleep, 50 ;
SendInput, {Enter} ;
Sleep, 50 ;
BlockInput, Off  ;
ExitApp