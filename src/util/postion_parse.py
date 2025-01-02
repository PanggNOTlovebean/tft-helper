
# 屏幕绝对位置转相对位置
def abs2relation(x: int, y: int, base_width: int = 2560, base_height: int = 1440):
    print(f"{(1.0 * x / base_width):.4f}, {(1.0 * y / base_height):.4f}")

if __name__ == "__main__":
    abs2relation(1711, 457)
    abs2relation(1945, 632)