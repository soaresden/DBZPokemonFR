import sys
def apply_ips(rom: bytearray, ips: bytes) -> bytearray:
    assert ips[:5]==b'PATCH'
    p=5
    while ips[p:p+3]!=b'EOF':
        off=int.from_bytes(ips[p:p+3],'big'); size=int.from_bytes(ips[p+3:p+5],'big'); p+=5
        if size==0:
            rle=int.from_bytes(ips[p:p+2],'big'); val=ips[p+2]; p+=3
            if off+rle>len(rom): rom.extend(b'\xff'*(off+rle-len(rom)))
            rom[off:off+rle]=bytes([val])*rle
        else:
            if off+size>len(rom): rom.extend(b'\xff'*(off+size-len(rom)))
            rom[off:off+size]=ips[p:p+size]; p+=size
    return rom
def make_ips(orig: bytes, new: bytes) -> bytes:
    out=bytearray(b'PATCH')
    n=max(len(orig),len(new)); i=0
    o=orig+b'\x00'*(n-len(orig)); 
    while i<n:
        if o[i]==new[i]: i+=1; continue
        j=i
        while j<n and j-i<0xFFFF and (o[j]!=new[j] or (j+1<n and j+1-i<0xFFFF and o[j+1]!=new[j+1]) ): j+=1
        # avoid offset equal to 'EOF' (0x454F46)
        if i==0x454F46: i-=1
        chunk=new[i:j]
        out+=i.to_bytes(3,'big')+len(chunk).to_bytes(2,'big')+chunk
        i=j
    out+=b'EOF'
    return bytes(out)
if __name__=='__main__':
    rom=bytearray(open(sys.argv[1],'rb').read()); ips=open(sys.argv[2],'rb').read()
    open(sys.argv[3],'wb').write(apply_ips(rom,ips))
