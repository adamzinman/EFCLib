"""Re-pack a generated project zip the way a Designer export looks: project.json first + folder entries."""
import zipfile, sys
def redo(src, dst):
    zin = zipfile.ZipFile(src); names = zin.namelist(); dirs = set()
    for n in names:
        parts = n.split('/')[:-1]
        for i in range(1, len(parts) + 1): dirs.add('/'.join(parts[:i]) + '/')
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('project.json', zin.read('project.json'))
        for d in sorted(dirs): z.writestr(zipfile.ZipInfo(d), '')
        for n in names:
            if n != 'project.json': z.writestr(n, zin.read(n))
if __name__ == "__main__": redo(sys.argv[1], sys.argv[2])
