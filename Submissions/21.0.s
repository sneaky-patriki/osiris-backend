main:
    li $t0, 0                   # int i = 0
    li $t1, 0                   # int j = 0
    li  $t2, 0                  # last_number = 0

loop1:
    bgt $t0, 9, endloop1       # if (i > 9) goto endloop1
    li  $v0, 5                 # scanf("%d");
    syscall

    li  $t1, 4
    mul $t1, $t0, $t1          # j = 4 * i
    sw  $v0, numbers($t1)      # &numbers[i] = input

    li  $t2, v0                 # last_number = numbers[i]

    add $t0, $t0, 1
    b   loop1

endloop1:
    li  $t0, 0              # i = 0

loop2:
    bgt $t0, 9, endloop2    # if (i > 9) goto endloop2
    add $t0, $t0, 1         # i++
    

endloop2:
    jr  $ra                 # return

    .data
numbers: .word 0 0 0 0 0 0 0 0 0 0
