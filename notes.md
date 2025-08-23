s = s₀;
c = nextChar();
while (c != eof) {
    s = move(s,c);
    c = nextChar();
}
if (s está em F) return "sim";
else return "não";