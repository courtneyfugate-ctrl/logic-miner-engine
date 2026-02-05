
def detect_p():
    lines = open('sandbox/v28_rigorous_audit_dump.txt', 'r', encoding='utf-8').readlines()
    addrs = []
    for l in lines:
        if '|' in l and 'ADDR' not in l and '---' not in l:
            try:
                addrs.append(int(l.split('|')[1].strip()))
            except:
                continue
    
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 31]:
        if all(a % p == 1 for a in addrs):
            print(f"Detected Prime: {p}")
            return p
    print("Prime not detected.")
    return None

if __name__ == "__main__":
    detect_p()
