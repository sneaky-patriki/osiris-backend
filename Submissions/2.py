def foo(n):
    yield 1
    if n < 2:
        return
    yield 2
    yield 3

print(list(foo(1)))
