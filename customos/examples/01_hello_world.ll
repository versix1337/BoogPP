; ModuleID = '01_hello_world'
source_filename = "01_hello_world.cos"

target triple = "x86_64-pc-windows-msvc"

define i32 @main() {
  entry:
    ret i32 0
    ret i32 0  ; default return
}


; Standard library declarations
declare void @print(i8*)
declare i8* @malloc(i64)
declare void @free(i8*)